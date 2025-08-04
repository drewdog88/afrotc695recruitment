const express = require('express');
const { body, validationResult, query } = require('express-validator');
const { getDatabase } = require('../database/init');
const { authenticateToken, logUserActivity } = require('../middleware/auth');
const { logger } = require('../utils/logger');

const router = express.Router();

// Get all potential recruits with filtering and pagination
router.get('/', [
  authenticateToken,
  logUserActivity('view', 'potential_recruits'),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('status').optional().isIn(['prospective', 'contacted', 'interested', 'applied', 'enrolled', 'not_interested']),
  query('school_type').optional().isIn(['high_school', 'college']),
  query('search').optional().isString()
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { page = 1, limit = 20, status, school_type, search } = req.query;
    const offset = (page - 1) * limit;
    const db = getDatabase();

    let whereClause = 'WHERE 1=1';
    let params = [];

    if (status) {
      whereClause += ' AND status = ?';
      params.push(status);
    }

    if (school_type) {
      whereClause += ' AND school_type = ?';
      params.push(school_type);
    }

    if (search) {
      whereClause += ' AND (first_name LIKE ? OR last_name LIKE ? OR current_school LIKE ? OR major LIKE ?)';
      const searchTerm = `%${search}%`;
      params.push(searchTerm, searchTerm, searchTerm, searchTerm);
    }

    // Get total count
    db.get(`SELECT COUNT(*) as total FROM potential_recruits ${whereClause}`, params, (err, countResult) => {
      if (err) {
        logger.error('Error counting recruits:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      // Get recruits with pagination
      const query = `
        SELECT 
          pr.*,
          u1.username as assigned_to_name,
          u2.username as created_by_name
        FROM potential_recruits pr
        LEFT JOIN users u1 ON pr.assigned_to = u1.id
        LEFT JOIN users u2 ON pr.created_by = u2.id
        ${whereClause}
        ORDER BY pr.created_at DESC
        LIMIT ? OFFSET ?
      `;

      db.all(query, [...params, limit, offset], (err, recruits) => {
        if (err) {
          logger.error('Error fetching recruits:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        res.json({
          recruits,
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
    logger.error('Error in recruits GET:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get single recruit by ID
router.get('/:id', [
  authenticateToken,
  logUserActivity('view', 'potential_recruits')
], (req, res) => {
  try {
    const { id } = req.params;
    const db = getDatabase();

    db.get(`
      SELECT 
        pr.*,
        u1.username as assigned_to_name,
        u2.username as created_by_name
      FROM potential_recruits pr
      LEFT JOIN users u1 ON pr.assigned_to = u1.id
      LEFT JOIN users u2 ON pr.created_by = u2.id
      WHERE pr.id = ?
    `, [id], (err, recruit) => {
      if (err) {
        logger.error('Error fetching recruit:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!recruit) {
        return res.status(404).json({ error: 'Recruit not found' });
      }

      res.json({ recruit });
    });
  } catch (error) {
    logger.error('Error in recruit GET by ID:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new potential recruit
router.post('/', [
  authenticateToken,
  logUserActivity('create', 'potential_recruits'),
  body('first_name').notEmpty().withMessage('First name is required'),
  body('last_name').notEmpty().withMessage('Last name is required'),
  body('current_school').notEmpty().withMessage('Current school is required'),
  body('school_type').isIn(['high_school', 'college']).withMessage('School type must be high_school or college'),
  body('email').optional().isEmail().withMessage('Invalid email format'),
  body('phone').optional().isMobilePhone().withMessage('Invalid phone format'),
  body('high_school_graduation_year').optional().isInt({ min: 2000, max: 2030 }),
  body('expected_college_graduation_year').optional().isInt({ min: 2020, max: 2035 }),
  body('gpa').optional().isFloat({ min: 0, max: 4.0 }),
  body('sat_score').optional().isInt({ min: 400, max: 1600 }),
  body('act_score').optional().isInt({ min: 1, max: 36 }),
  body('status').optional().isIn(['prospective', 'contacted', 'interested', 'applied', 'enrolled', 'not_interested'])
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const recruitData = {
      ...req.body,
      created_by: req.user.id,
      assigned_to: req.body.assigned_to || req.user.id
    };

    const db = getDatabase();
    const fields = Object.keys(recruitData).join(', ');
    const placeholders = Object.keys(recruitData).map(() => '?').join(', ');
    const values = Object.values(recruitData);

    db.run(
      `INSERT INTO potential_recruits (${fields}) VALUES (${placeholders})`,
      values,
      function(err) {
        if (err) {
          logger.error('Error creating recruit:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        // Get the created recruit
        db.get('SELECT * FROM potential_recruits WHERE id = ?', [this.lastID], (err, recruit) => {
          if (err) {
            logger.error('Error fetching created recruit:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          logger.info(`Recruit created: ${recruit.first_name} ${recruit.last_name} by user: ${req.user.username}`);
          res.status(201).json({ recruit, message: 'Recruit created successfully' });
        });
      }
    );
  } catch (error) {
    logger.error('Error in recruit POST:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update potential recruit
router.put('/:id', [
  authenticateToken,
  logUserActivity('update', 'potential_recruits'),
  body('first_name').optional().notEmpty().withMessage('First name cannot be empty'),
  body('last_name').optional().notEmpty().withMessage('Last name cannot be empty'),
  body('email').optional().isEmail().withMessage('Invalid email format'),
  body('phone').optional().isMobilePhone().withMessage('Invalid phone format'),
  body('school_type').optional().isIn(['high_school', 'college']).withMessage('School type must be high_school or college'),
  body('status').optional().isIn(['prospective', 'contacted', 'interested', 'applied', 'enrolled', 'not_interested'])
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { id } = req.params;
    const updateData = { ...req.body, updated_at: new Date().toISOString() };
    const db = getDatabase();

    // Check if recruit exists
    db.get('SELECT id FROM potential_recruits WHERE id = ?', [id], (err, recruit) => {
      if (err) {
        logger.error('Error checking recruit existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!recruit) {
        return res.status(404).json({ error: 'Recruit not found' });
      }

      const fields = Object.keys(updateData).map(key => `${key} = ?`).join(', ');
      const values = [...Object.values(updateData), id];

      db.run(
        `UPDATE potential_recruits SET ${fields} WHERE id = ?`,
        values,
        function(err) {
          if (err) {
            logger.error('Error updating recruit:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          // Get updated recruit
          db.get('SELECT * FROM potential_recruits WHERE id = ?', [id], (err, updatedRecruit) => {
            if (err) {
              logger.error('Error fetching updated recruit:', err);
              return res.status(500).json({ error: 'Internal server error' });
            }

            logger.info(`Recruit updated: ${updatedRecruit.first_name} ${updatedRecruit.last_name} by user: ${req.user.username}`);
            res.json({ recruit: updatedRecruit, message: 'Recruit updated successfully' });
          });
        }
      );
    });
  } catch (error) {
    logger.error('Error in recruit PUT:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete potential recruit
router.delete('/:id', [
  authenticateToken,
  logUserActivity('delete', 'potential_recruits')
], (req, res) => {
  try {
    const { id } = req.params;
    const db = getDatabase();

    // Check if recruit exists
    db.get('SELECT first_name, last_name FROM potential_recruits WHERE id = ?', [id], (err, recruit) => {
      if (err) {
        logger.error('Error checking recruit existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!recruit) {
        return res.status(404).json({ error: 'Recruit not found' });
      }

      db.run('DELETE FROM potential_recruits WHERE id = ?', [id], function(err) {
        if (err) {
          logger.error('Error deleting recruit:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        logger.info(`Recruit deleted: ${recruit.first_name} ${recruit.last_name} by user: ${req.user.username}`);
        res.json({ message: 'Recruit deleted successfully' });
      });
    });
  } catch (error) {
    logger.error('Error in recruit DELETE:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get recruitment statistics
router.get('/stats/overview', [
  authenticateToken,
  logUserActivity('view', 'recruit_stats')
], (req, res) => {
  try {
    const db = getDatabase();
    
    const queries = {
      total: 'SELECT COUNT(*) as count FROM potential_recruits',
      byStatus: 'SELECT status, COUNT(*) as count FROM potential_recruits GROUP BY status',
      bySchoolType: 'SELECT school_type, COUNT(*) as count FROM potential_recruits GROUP BY school_type',
      byYear: 'SELECT expected_college_graduation_year, COUNT(*) as count FROM potential_recruits WHERE expected_college_graduation_year IS NOT NULL GROUP BY expected_college_graduation_year ORDER BY expected_college_graduation_year',
      recent: 'SELECT COUNT(*) as count FROM potential_recruits WHERE created_at >= date("now", "-30 days")'
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
    logger.error('Error in recruit stats:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router; 