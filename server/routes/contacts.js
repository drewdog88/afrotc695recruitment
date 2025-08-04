const express = require('express');
const { body, validationResult, query } = require('express-validator');
const { getDatabase } = require('../database/init');
const { authenticateToken, logUserActivity } = require('../middleware/auth');
const { logger } = require('../utils/logger');

const router = express.Router();

// Get all university contacts
router.get('/', [
  authenticateToken,
  logUserActivity('view', 'university_contacts'),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('is_active').optional().isBoolean(),
  query('search').optional().isString()
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { page = 1, limit = 20, is_active, search } = req.query;
    const offset = (page - 1) * limit;
    const db = getDatabase();

    let whereClause = 'WHERE 1=1';
    let params = [];

    if (is_active !== undefined) {
      whereClause += ' AND is_active = ?';
      params.push(is_active === 'true' ? 1 : 0);
    }

    if (search) {
      whereClause += ' AND (university_name LIKE ? OR contact_name LIKE ? OR contact_title LIKE ?)';
      const searchTerm = `%${search}%`;
      params.push(searchTerm, searchTerm, searchTerm);
    }

    // Get total count
    db.get(`SELECT COUNT(*) as total FROM university_contacts ${whereClause}`, params, (err, countResult) => {
      if (err) {
        logger.error('Error counting contacts:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      // Get contacts with pagination
      const query = `
        SELECT * FROM university_contacts
        ${whereClause}
        ORDER BY university_name, contact_name
        LIMIT ? OFFSET ?
      `;

      db.all(query, [...params, limit, offset], (err, contacts) => {
        if (err) {
          logger.error('Error fetching contacts:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        res.json({
          contacts,
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
    logger.error('Error in contacts GET:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get single contact by ID
router.get('/:id', [
  authenticateToken,
  logUserActivity('view', 'university_contacts')
], (req, res) => {
  try {
    const { id } = req.params;
    const db = getDatabase();

    db.get('SELECT * FROM university_contacts WHERE id = ?', [id], (err, contact) => {
      if (err) {
        logger.error('Error fetching contact:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!contact) {
        return res.status(404).json({ error: 'Contact not found' });
      }

      res.json({ contact });
    });
  } catch (error) {
    logger.error('Error in contact GET by ID:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new university contact
router.post('/', [
  authenticateToken,
  logUserActivity('create', 'university_contacts'),
  body('university_name').notEmpty().withMessage('University name is required'),
  body('contact_name').notEmpty().withMessage('Contact name is required'),
  body('email').isEmail().withMessage('Valid email is required'),
  body('contact_title').optional().isString(),
  body('phone').optional().isMobilePhone().withMessage('Invalid phone format'),
  body('address').optional().isString(),
  body('notes').optional().isString()
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const contactData = {
      ...req.body,
      is_active: req.body.is_active !== false // Default to true
    };

    const db = getDatabase();
    const fields = Object.keys(contactData).join(', ');
    const placeholders = Object.keys(contactData).map(() => '?').join(', ');
    const values = Object.values(contactData);

    db.run(
      `INSERT INTO university_contacts (${fields}) VALUES (${placeholders})`,
      values,
      function(err) {
        if (err) {
          logger.error('Error creating contact:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        // Get the created contact
        db.get('SELECT * FROM university_contacts WHERE id = ?', [this.lastID], (err, contact) => {
          if (err) {
            logger.error('Error fetching created contact:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          logger.info(`Contact created: ${contact.contact_name} at ${contact.university_name} by user: ${req.user.username}`);
          res.status(201).json({ contact, message: 'Contact created successfully' });
        });
      }
    );
  } catch (error) {
    logger.error('Error in contact POST:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update university contact
router.put('/:id', [
  authenticateToken,
  logUserActivity('update', 'university_contacts'),
  body('university_name').optional().notEmpty().withMessage('University name cannot be empty'),
  body('contact_name').optional().notEmpty().withMessage('Contact name cannot be empty'),
  body('email').optional().isEmail().withMessage('Invalid email format'),
  body('phone').optional().isMobilePhone().withMessage('Invalid phone format')
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { id } = req.params;
    const updateData = { ...req.body, updated_at: new Date().toISOString() };
    const db = getDatabase();

    // Check if contact exists
    db.get('SELECT id FROM university_contacts WHERE id = ?', [id], (err, contact) => {
      if (err) {
        logger.error('Error checking contact existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!contact) {
        return res.status(404).json({ error: 'Contact not found' });
      }

      const fields = Object.keys(updateData).map(key => `${key} = ?`).join(', ');
      const values = [...Object.values(updateData), id];

      db.run(
        `UPDATE university_contacts SET ${fields} WHERE id = ?`,
        values,
        function(err) {
          if (err) {
            logger.error('Error updating contact:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          // Get updated contact
          db.get('SELECT * FROM university_contacts WHERE id = ?', [id], (err, updatedContact) => {
            if (err) {
              logger.error('Error fetching updated contact:', err);
              return res.status(500).json({ error: 'Internal server error' });
            }

            logger.info(`Contact updated: ${updatedContact.contact_name} at ${updatedContact.university_name} by user: ${req.user.username}`);
            res.json({ contact: updatedContact, message: 'Contact updated successfully' });
          });
        }
      );
    });
  } catch (error) {
    logger.error('Error in contact PUT:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete university contact
router.delete('/:id', [
  authenticateToken,
  logUserActivity('delete', 'university_contacts')
], (req, res) => {
  try {
    const { id } = req.params;
    const db = getDatabase();

    // Check if contact exists
    db.get('SELECT contact_name, university_name FROM university_contacts WHERE id = ?', [id], (err, contact) => {
      if (err) {
        logger.error('Error checking contact existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!contact) {
        return res.status(404).json({ error: 'Contact not found' });
      }

      db.run('DELETE FROM university_contacts WHERE id = ?', [id], function(err) {
        if (err) {
          logger.error('Error deleting contact:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        logger.info(`Contact deleted: ${contact.contact_name} at ${contact.university_name} by user: ${req.user.username}`);
        res.json({ message: 'Contact deleted successfully' });
      });
    });
  } catch (error) {
    logger.error('Error in contact DELETE:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router; 