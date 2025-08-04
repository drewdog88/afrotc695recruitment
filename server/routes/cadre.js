const express = require('express');
const { body, validationResult, query } = require('express-validator');
const { getDatabase } = require('../database/init');
const { authenticateToken, logUserActivity } = require('../middleware/auth');
const { logger } = require('../utils/logger');

const router = express.Router();

// Get all cadre with filtering and pagination
router.get('/', [
  authenticateToken,
  logUserActivity('view', 'cadre'),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('is_enrolled').optional().isBoolean(),
  query('graduation_year').optional().isInt({ min: 2020, max: 2030 }),
  query('search').optional().isString()
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { page = 1, limit = 20, is_enrolled, graduation_year, search } = req.query;
    const offset = (page - 1) * limit;
    const db = getDatabase();

    let whereClause = 'WHERE 1=1';
    let params = [];

    if (is_enrolled !== undefined) {
      whereClause += ' AND is_enrolled = ?';
      params.push(is_enrolled === 'true' ? 1 : 0);
    }

    if (graduation_year) {
      whereClause += ' AND graduation_year = ?';
      params.push(graduation_year);
    }

    if (search) {
      whereClause += ' AND (first_name LIKE ? OR last_name LIKE ? OR major LIKE ? OR hometown LIKE ?)';
      const searchTerm = `%${search}%`;
      params.push(searchTerm, searchTerm, searchTerm, searchTerm);
    }

    // Get total count
    db.get(`SELECT COUNT(*) as total FROM cadre ${whereClause}`, params, (err, countResult) => {
      if (err) {
        logger.error('Error counting cadre:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      // Get cadre with pagination
      const query = `
        SELECT * FROM cadre
        ${whereClause}
        ORDER BY last_name, first_name
        LIMIT ? OFFSET ?
      `;

      db.all(query, [...params, limit, offset], (err, cadre) => {
        if (err) {
          logger.error('Error fetching cadre:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        res.json({
          cadre,
          pagination: {
            page: parseInt(page),
            limit: parseInt(limit),
            total: countResult.total,
            pages: Math.ceil(countResult.total / limit)
          }
        });
      });
    });
  } catch (error) {
    logger.error('Error in cadre GET:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get single cadre by ID
router.get('/:id', [
  authenticateToken,
  logUserActivity('view', 'cadre')
], (req, res) => {
  try {
    const { id } = req.params;
    const db = getDatabase();

    db.get('SELECT * FROM cadre WHERE id = ?', [id], (err, cadre) => {
      if (err) {
        logger.error('Error fetching cadre:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!cadre) {
        return res.status(404).json({ error: 'Cadre not found' });
      }

      res.json({ cadre });
    });
  } catch (error) {
    logger.error('Error in cadre GET by ID:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new cadre
router.post('/', [
  authenticateToken,
  logUserActivity('create', 'cadre'),
  body('first_name').notEmpty().withMessage('First name is required'),
  body('last_name').notEmpty().withMessage('Last name is required'),
  body('email').isEmail().withMessage('Valid email is required'),
  body('major').notEmpty().withMessage('Major is required'),
  body('graduation_year').isInt({ min: 2020, max: 2030 }).withMessage('Valid graduation year is required'),
  body('cadet_rank').notEmpty().withMessage('Cadet rank is required'),
  body('phone').optional().isMobilePhone().withMessage('Invalid phone format'),
  body('hometown').optional().isString(),
  body('officer_interest').optional().isString(),
  body('gpa').optional().isFloat({ min: 0, max: 4.0 }),
  body('is_enrolled').optional().isBoolean()
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const cadreData = {
      ...req.body,
      is_enrolled: req.body.is_enrolled !== false // Default to true
    };

    const db = getDatabase();
    const fields = Object.keys(cadreData).join(', ');
    const placeholders = Object.keys(cadreData).map(() => '?').join(', ');
    const values = Object.values(cadreData);

    db.run(
      `INSERT INTO cadre (${fields}) VALUES (${placeholders})`,
      values,
      function(err) {
        if (err) {
          logger.error('Error creating cadre:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        // Get the created cadre
        db.get('SELECT * FROM cadre WHERE id = ?', [this.lastID], (err, cadre) => {
          if (err) {
            logger.error('Error fetching created cadre:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          logger.info(`Cadre created: ${cadre.first_name} ${cadre.last_name} by user: ${req.user.username}`);
          res.status(201).json({ cadre, message: 'Cadre created successfully' });
        });
      }
    );
  } catch (error) {
    logger.error('Error in cadre POST:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update cadre
router.put('/:id', [
  authenticateToken,
  logUserActivity('update', 'cadre'),
  body('first_name').optional().notEmpty().withMessage('First name cannot be empty'),
  body('last_name').optional().notEmpty().withMessage('Last name cannot be empty'),
  body('email').optional().isEmail().withMessage('Invalid email format'),
  body('phone').optional().isMobilePhone().withMessage('Invalid phone format'),
  body('graduation_year').optional().isInt({ min: 2020, max: 2030 }),
  body('gpa').optional().isFloat({ min: 0, max: 4.0 })
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { id } = req.params;
    const updateData = { ...req.body, updated_at: new Date().toISOString() };
    const db = getDatabase();

    // Check if cadre exists
    db.get('SELECT id FROM cadre WHERE id = ?', [id], (err, cadre) => {
      if (err) {
        logger.error('Error checking cadre existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!cadre) {
        return res.status(404).json({ error: 'Cadre not found' });
      }

      const fields = Object.keys(updateData).map(key => `${key} = ?`).join(', ');
      const values = [...Object.values(updateData), id];

      db.run(
        `UPDATE cadre SET ${fields} WHERE id = ?`,
        values,
        function(err) {
          if (err) {
            logger.error('Error updating cadre:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          // Get updated cadre
          db.get('SELECT * FROM cadre WHERE id = ?', [id], (err, updatedCadre) => {
            if (err) {
              logger.error('Error fetching updated cadre:', err);
              return res.status(500).json({ error: 'Internal server error' });
            }

            logger.info(`Cadre updated: ${updatedCadre.first_name} ${updatedCadre.last_name} by user: ${req.user.username}`);
            res.json({ cadre: updatedCadre, message: 'Cadre updated successfully' });
          });
        }
      );
    });
  } catch (error) {
    logger.error('Error in cadre PUT:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update enrollment status
router.patch('/:id/enrollment', [
  authenticateToken,
  logUserActivity('update_enrollment', 'cadre'),
  body('is_enrolled').isBoolean().withMessage('Enrollment status is required'),
  body('unenrollment_reason').optional().isString(),
  body('unenrollment_date').optional().isISO8601().withMessage('Invalid date format')
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { id } = req.params;
    const { is_enrolled, unenrollment_reason, unenrollment_date } = req.body;
    const db = getDatabase();

    // Check if cadre exists
    db.get('SELECT first_name, last_name FROM cadre WHERE id = ?', [id], (err, cadre) => {
      if (err) {
        logger.error('Error checking cadre existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!cadre) {
        return res.status(404).json({ error: 'Cadre not found' });
      }

      const updateData = {
        is_enrolled: is_enrolled ? 1 : 0,
        updated_at: new Date().toISOString()
      };

      if (!is_enrolled) {
        updateData.unenrollment_reason = unenrollment_reason || null;
        updateData.unenrollment_date = unenrollment_date || new Date().toISOString().split('T')[0];
      } else {
        updateData.unenrollment_reason = null;
        updateData.unenrollment_date = null;
      }

      const fields = Object.keys(updateData).map(key => `${key} = ?`).join(', ');
      const values = [...Object.values(updateData), id];

      db.run(
        `UPDATE cadre SET ${fields} WHERE id = ?`,
        values,
        function(err) {
          if (err) {
            logger.error('Error updating cadre enrollment:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          logger.info(`Cadre enrollment updated: ${cadre.first_name} ${cadre.last_name} - Enrolled: ${is_enrolled} by user: ${req.user.username}`);
          res.json({ 
            message: `Cadre ${is_enrolled ? 'enrolled' : 'unenrolled'} successfully`,
            is_enrolled,
            unenrollment_reason: updateData.unenrollment_reason,
            unenrollment_date: updateData.unenrollment_date
          });
        }
      );
    });
  } catch (error) {
    logger.error('Error in cadre enrollment PATCH:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete cadre
router.delete('/:id', [
  authenticateToken,
  logUserActivity('delete', 'cadre')
], (req, res) => {
  try {
    const { id } = req.params;
    const db = getDatabase();

    // Check if cadre exists
    db.get('SELECT first_name, last_name FROM cadre WHERE id = ?', [id], (err, cadre) => {
      if (err) {
        logger.error('Error checking cadre existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!cadre) {
        return res.status(404).json({ error: 'Cadre not found' });
      }

      db.run('DELETE FROM cadre WHERE id = ?', [id], function(err) {
        if (err) {
          logger.error('Error deleting cadre:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        logger.info(`Cadre deleted: ${cadre.first_name} ${cadre.last_name} by user: ${req.user.username}`);
        res.json({ message: 'Cadre deleted successfully' });
      });
    });
  } catch (error) {
    logger.error('Error in cadre DELETE:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get cadre statistics
router.get('/stats/overview', [
  authenticateToken,
  logUserActivity('view', 'cadre_stats')
], (req, res) => {
  try {
    const db = getDatabase();
    
    const queries = {
      total: 'SELECT COUNT(*) as count FROM cadre',
      enrolled: 'SELECT COUNT(*) as count FROM cadre WHERE is_enrolled = 1',
      unenrolled: 'SELECT COUNT(*) as count FROM cadre WHERE is_enrolled = 0',
      byGraduationYear: 'SELECT graduation_year, COUNT(*) as count FROM cadre GROUP BY graduation_year ORDER BY graduation_year',
      byRank: 'SELECT cadet_rank, COUNT(*) as count FROM cadre GROUP BY cadet_rank ORDER BY cadet_rank',
      byMajor: 'SELECT major, COUNT(*) as count FROM cadre GROUP BY major ORDER BY count DESC LIMIT 10',
      averageGPA: 'SELECT AVG(gpa) as average FROM cadre WHERE gpa IS NOT NULL'
    };

    const results = {};
    let completed = 0;
    const total = Object.keys(queries).length;

    Object.entries(queries).forEach(([key, query]) => {
      db.all(query, [], (err, rows) => {
        if (err) {
          logger.error(`Error fetching ${key} stats:`, err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        results[key] = rows;
        completed++;

        if (completed === total) {
          res.json({ stats: results });
        }
      });
    });
  } catch (error) {
    logger.error('Error in cadre stats:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router; 