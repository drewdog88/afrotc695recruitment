const express = require('express');
const { body, validationResult, query } = require('express-validator');
const { getDatabase } = require('../database/init');
const { authenticateToken, logUserActivity } = require('../middleware/auth');
const { logger } = require('../utils/logger');

const router = express.Router();

// Get all recruitment events with filtering
router.get('/', [
  authenticateToken,
  logUserActivity('view', 'recruitment_events'),
  query('start_date').optional().isISO8601().withMessage('Invalid start date format'),
  query('end_date').optional().isISO8601().withMessage('Invalid end date format'),
  query('event_type').optional().isIn(['info_session', 'career_fair', 'campus_visit', 'other']),
  query('status').optional().isIn(['scheduled', 'completed', 'cancelled']),
  query('university_id').optional().isInt({ min: 1 })
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { start_date, end_date, event_type, status, university_id } = req.query;
    const db = getDatabase();

    let whereClause = 'WHERE 1=1';
    let params = [];

    if (start_date) {
      whereClause += ' AND event_date >= ?';
      params.push(start_date);
    }

    if (end_date) {
      whereClause += ' AND event_date <= ?';
      params.push(end_date);
    }

    if (event_type) {
      whereClause += ' AND event_type = ?';
      params.push(event_type);
    }

    if (status) {
      whereClause += ' AND status = ?';
      params.push(status);
    }

    if (university_id) {
      whereClause += ' AND university_id = ?';
      params.push(university_id);
    }

    const query = `
      SELECT 
        re.*,
        uc.university_name,
        uc.contact_name,
        u.username as created_by_name
      FROM recruitment_events re
      LEFT JOIN university_contacts uc ON re.university_id = uc.id
      LEFT JOIN users u ON re.created_by = u.id
      ${whereClause}
      ORDER BY re.event_date DESC, re.start_time
    `;

    db.all(query, params, (err, events) => {
      if (err) {
        logger.error('Error fetching events:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      res.json({ events });
    });
  } catch (error) {
    logger.error('Error in calendar GET:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get single event by ID
router.get('/:id', [
  authenticateToken,
  logUserActivity('view', 'recruitment_events')
], (req, res) => {
  try {
    const { id } = req.params;
    const db = getDatabase();

    db.get(`
      SELECT 
        re.*,
        uc.university_name,
        uc.contact_name,
        u.username as created_by_name
      FROM recruitment_events re
      LEFT JOIN university_contacts uc ON re.university_id = uc.id
      LEFT JOIN users u ON re.created_by = u.id
      WHERE re.id = ?
    `, [id], (err, event) => {
      if (err) {
        logger.error('Error fetching event:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!event) {
        return res.status(404).json({ error: 'Event not found' });
      }

      res.json({ event });
    });
  } catch (error) {
    logger.error('Error in event GET by ID:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new recruitment event
router.post('/', [
  authenticateToken,
  logUserActivity('create', 'recruitment_events'),
  body('title').notEmpty().withMessage('Event title is required'),
  body('event_date').isISO8601().withMessage('Valid event date is required'),
  body('event_type').isIn(['info_session', 'career_fair', 'campus_visit', 'other']).withMessage('Valid event type is required'),
  body('description').optional().isString(),
  body('start_time').optional().matches(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/).withMessage('Start time must be in HH:MM format'),
  body('end_time').optional().matches(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/).withMessage('End time must be in HH:MM format'),
  body('location').optional().isString(),
  body('university_id').optional().isInt({ min: 1 }),
  body('status').optional().isIn(['scheduled', 'completed', 'cancelled']),
  body('notes').optional().isString()
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const eventData = {
      ...req.body,
      created_by: req.user.id,
      status: req.body.status || 'scheduled',
      attendees_count: req.body.attendees_count || 0
    };

    const db = getDatabase();
    const fields = Object.keys(eventData).join(', ');
    const placeholders = Object.keys(eventData).map(() => '?').join(', ');
    const values = Object.values(eventData);

    db.run(
      `INSERT INTO recruitment_events (${fields}) VALUES (${placeholders})`,
      values,
      function(err) {
        if (err) {
          logger.error('Error creating event:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        // Get the created event
        db.get(`
          SELECT 
            re.*,
            uc.university_name,
            uc.contact_name,
            u.username as created_by_name
          FROM recruitment_events re
          LEFT JOIN university_contacts uc ON re.university_id = uc.id
          LEFT JOIN users u ON re.created_by = u.id
          WHERE re.id = ?
        `, [this.lastID], (err, event) => {
          if (err) {
            logger.error('Error fetching created event:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          logger.info(`Event created: ${event.title} by user: ${req.user.username}`);
          res.status(201).json({ event, message: 'Event created successfully' });
        });
      }
    );
  } catch (error) {
    logger.error('Error in event POST:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update recruitment event
router.put('/:id', [
  authenticateToken,
  logUserActivity('update', 'recruitment_events'),
  body('title').optional().notEmpty().withMessage('Event title cannot be empty'),
  body('event_date').optional().isISO8601().withMessage('Invalid event date format'),
  body('event_type').optional().isIn(['info_session', 'career_fair', 'campus_visit', 'other']),
  body('start_time').optional().matches(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/).withMessage('Start time must be in HH:MM format'),
  body('end_time').optional().matches(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/).withMessage('End time must be in HH:MM format'),
  body('status').optional().isIn(['scheduled', 'completed', 'cancelled'])
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { id } = req.params;
    const updateData = { ...req.body, updated_at: new Date().toISOString() };
    const db = getDatabase();

    // Check if event exists
    db.get('SELECT id FROM recruitment_events WHERE id = ?', [id], (err, event) => {
      if (err) {
        logger.error('Error checking event existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!event) {
        return res.status(404).json({ error: 'Event not found' });
      }

      const fields = Object.keys(updateData).map(key => `${key} = ?`).join(', ');
      const values = [...Object.values(updateData), id];

      db.run(
        `UPDATE recruitment_events SET ${fields} WHERE id = ?`,
        values,
        function(err) {
          if (err) {
            logger.error('Error updating event:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          // Get updated event
          db.get(`
            SELECT 
              re.*,
              uc.university_name,
              uc.contact_name,
              u.username as created_by_name
            FROM recruitment_events re
            LEFT JOIN university_contacts uc ON re.university_id = uc.id
            LEFT JOIN users u ON re.created_by = u.id
            WHERE re.id = ?
          `, [id], (err, updatedEvent) => {
            if (err) {
              logger.error('Error fetching updated event:', err);
              return res.status(500).json({ error: 'Internal server error' });
            }

            logger.info(`Event updated: ${updatedEvent.title} by user: ${req.user.username}`);
            res.json({ event: updatedEvent, message: 'Event updated successfully' });
          });
        }
      );
    });
  } catch (error) {
    logger.error('Error in event PUT:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update event status
router.patch('/:id/status', [
  authenticateToken,
  logUserActivity('update_status', 'recruitment_events'),
  body('status').isIn(['scheduled', 'completed', 'cancelled']).withMessage('Valid status is required'),
  body('attendees_count').optional().isInt({ min: 0 }),
  body('notes').optional().isString()
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { id } = req.params;
    const { status, attendees_count, notes } = req.body;
    const db = getDatabase();

    // Check if event exists
    db.get('SELECT title FROM recruitment_events WHERE id = ?', [id], (err, event) => {
      if (err) {
        logger.error('Error checking event existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!event) {
        return res.status(404).json({ error: 'Event not found' });
      }

      const updateData = {
        status,
        updated_at: new Date().toISOString()
      };

      if (attendees_count !== undefined) {
        updateData.attendees_count = attendees_count;
      }

      if (notes !== undefined) {
        updateData.notes = notes;
      }

      const fields = Object.keys(updateData).map(key => `${key} = ?`).join(', ');
      const values = [...Object.values(updateData), id];

      db.run(
        `UPDATE recruitment_events SET ${fields} WHERE id = ?`,
        values,
        function(err) {
          if (err) {
            logger.error('Error updating event status:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          logger.info(`Event status updated: ${event.title} - ${status} by user: ${req.user.username}`);
          res.json({ 
            message: `Event status updated to ${status}`,
            status,
            attendees_count: updateData.attendees_count,
            notes: updateData.notes
          });
        }
      );
    });
  } catch (error) {
    logger.error('Error in event status PATCH:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete recruitment event
router.delete('/:id', [
  authenticateToken,
  logUserActivity('delete', 'recruitment_events')
], (req, res) => {
  try {
    const { id } = req.params;
    const db = getDatabase();

    // Check if event exists
    db.get('SELECT title FROM recruitment_events WHERE id = ?', [id], (err, event) => {
      if (err) {
        logger.error('Error checking event existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!event) {
        return res.status(404).json({ error: 'Event not found' });
      }

      db.run('DELETE FROM recruitment_events WHERE id = ?', [id], function(err) {
        if (err) {
          logger.error('Error deleting event:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        logger.info(`Event deleted: ${event.title} by user: ${req.user.username}`);
        res.json({ message: 'Event deleted successfully' });
      });
    });
  } catch (error) {
    logger.error('Error in event DELETE:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get calendar statistics
router.get('/stats/overview', [
  authenticateToken,
  logUserActivity('view', 'calendar_stats')
], (req, res) => {
  try {
    const db = getDatabase();
    
    const queries = {
      total: 'SELECT COUNT(*) as count FROM recruitment_events',
      upcoming: 'SELECT COUNT(*) as count FROM recruitment_events WHERE event_date >= date("now") AND status = "scheduled"',
      completed: 'SELECT COUNT(*) as count FROM recruitment_events WHERE status = "completed"',
      byType: 'SELECT event_type, COUNT(*) as count FROM recruitment_events GROUP BY event_type',
      byMonth: 'SELECT strftime("%Y-%m", event_date) as month, COUNT(*) as count FROM recruitment_events GROUP BY month ORDER BY month DESC LIMIT 12',
      totalAttendees: 'SELECT SUM(attendees_count) as total FROM recruitment_events WHERE status = "completed"'
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
    logger.error('Error in calendar stats:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router; 