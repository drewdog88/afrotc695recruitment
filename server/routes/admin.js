const express = require('express');
const bcrypt = require('bcryptjs');
const { body, validationResult, query } = require('express-validator');
const { getDatabase } = require('../database/init');
const { authenticateToken, requireAdmin, logUserActivity } = require('../middleware/auth');
const { logger } = require('../utils/logger');

const router = express.Router();

// All admin routes require admin privileges
router.use(authenticateToken, requireAdmin);

// Get all users
router.get('/users', [
  logUserActivity('view', 'admin_users'),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('role').optional().isIn(['admin', 'user']),
  query('is_active').optional().isBoolean()
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { page = 1, limit = 20, role, is_active } = req.query;
    const offset = (page - 1) * limit;
    const db = getDatabase();

    let whereClause = 'WHERE 1=1';
    let params = [];

    if (role) {
      whereClause += ' AND role = ?';
      params.push(role);
    }

    if (is_active !== undefined) {
      whereClause += ' AND is_active = ?';
      params.push(is_active === 'true' ? 1 : 0);
    }

    // Get total count
    db.get(`SELECT COUNT(*) as total FROM users ${whereClause}`, params, (err, countResult) => {
      if (err) {
        logger.error('Error counting users:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      // Get users with pagination (exclude password_hash)
      const query = `
        SELECT id, username, email, role, is_active, created_at, last_login, login_count
        FROM users
        ${whereClause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
      `;

      db.all(query, [...params, limit, offset], (err, users) => {
        if (err) {
          logger.error('Error fetching users:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        res.json({
          users,
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
    logger.error('Error in admin users GET:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new user
router.post('/users', [
  logUserActivity('create', 'admin_users'),
  body('username').notEmpty().withMessage('Username is required'),
  body('email').isEmail().withMessage('Valid email is required'),
  body('password').isLength({ min: 8 }).withMessage('Password must be at least 8 characters long'),
  body('role').isIn(['admin', 'user']).withMessage('Role must be admin or user')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { username, email, password, role } = req.body;
    const db = getDatabase();

    // Check if username or email already exists
    db.get('SELECT id FROM users WHERE username = ? OR email = ?', [username, email], async (err, existingUser) => {
      if (err) {
        logger.error('Error checking user existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (existingUser) {
        return res.status(400).json({ error: 'Username or email already exists' });
      }

      // Hash password
      const passwordHash = await bcrypt.hash(password, 12);

      // Create user
      db.run(
        'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
        [username, email, passwordHash, role],
        function(err) {
          if (err) {
            logger.error('Error creating user:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          // Get the created user (without password)
          db.get(
            'SELECT id, username, email, role, is_active, created_at FROM users WHERE id = ?',
            [this.lastID],
            (err, user) => {
              if (err) {
                logger.error('Error fetching created user:', err);
                return res.status(500).json({ error: 'Internal server error' });
              }

              logger.info(`User created: ${user.username} with role: ${user.role} by admin: ${req.user.username}`);
              res.status(201).json({ user, message: 'User created successfully' });
            }
          );
        }
      );
    });
  } catch (error) {
    logger.error('Error in admin user POST:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update user
router.put('/users/:id', [
  logUserActivity('update', 'admin_users'),
  body('username').optional().notEmpty().withMessage('Username cannot be empty'),
  body('email').optional().isEmail().withMessage('Invalid email format'),
  body('role').optional().isIn(['admin', 'user']).withMessage('Role must be admin or user'),
  body('is_active').optional().isBoolean()
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { id } = req.params;
    const updateData = { ...req.body, updated_at: new Date().toISOString() };
    const db = getDatabase();

    // Check if user exists
    db.get('SELECT username FROM users WHERE id = ?', [id], (err, user) => {
      if (err) {
        logger.error('Error checking user existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      // Prevent admin from deactivating themselves
      if (id == req.user.id && updateData.is_active === false) {
        return res.status(400).json({ error: 'Cannot deactivate your own account' });
      }

      const fields = Object.keys(updateData).map(key => `${key} = ?`).join(', ');
      const values = [...Object.values(updateData), id];

      db.run(
        `UPDATE users SET ${fields} WHERE id = ?`,
        values,
        function(err) {
          if (err) {
            logger.error('Error updating user:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          // Get updated user
          db.get(
            'SELECT id, username, email, role, is_active, created_at, last_login, login_count FROM users WHERE id = ?',
            [id],
            (err, updatedUser) => {
              if (err) {
                logger.error('Error fetching updated user:', err);
                return res.status(500).json({ error: 'Internal server error' });
              }

              logger.info(`User updated: ${updatedUser.username} by admin: ${req.user.username}`);
              res.json({ user: updatedUser, message: 'User updated successfully' });
            }
          );
        }
      );
    });
  } catch (error) {
    logger.error('Error in admin user PUT:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Reset user password
router.post('/users/:id/reset-password', [
  logUserActivity('reset_password', 'admin_users'),
  body('newPassword').isLength({ min: 8 }).withMessage('Password must be at least 8 characters long')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { id } = req.params;
    const { newPassword } = req.body;
    const db = getDatabase();

    // Check if user exists
    db.get('SELECT username FROM users WHERE id = ?', [id], async (err, user) => {
      if (err) {
        logger.error('Error checking user existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      // Hash new password
      const passwordHash = await bcrypt.hash(newPassword, 12);

      // Update password
      db.run(
        'UPDATE users SET password_hash = ? WHERE id = ?',
        [passwordHash, id],
        function(err) {
          if (err) {
            logger.error('Error resetting password:', err);
            return res.status(500).json({ error: 'Internal server error' });
          }

          logger.info(`Password reset for user: ${user.username} by admin: ${req.user.username}`);
          res.json({ message: 'Password reset successfully' });
        }
      );
    });
  } catch (error) {
    logger.error('Error in admin password reset:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete user
router.delete('/users/:id', [
  logUserActivity('delete', 'admin_users')
], (req, res) => {
  try {
    const { id } = req.params;
    const db = getDatabase();

    // Prevent admin from deleting themselves
    if (id == req.user.id) {
      return res.status(400).json({ error: 'Cannot delete your own account' });
    }

    // Check if user exists
    db.get('SELECT username FROM users WHERE id = ?', [id], (err, user) => {
      if (err) {
        logger.error('Error checking user existence:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      db.run('DELETE FROM users WHERE id = ?', [id], function(err) {
        if (err) {
          logger.error('Error deleting user:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        logger.info(`User deleted: ${user.username} by admin: ${req.user.username}`);
        res.json({ message: 'User deleted successfully' });
      });
    });
  } catch (error) {
    logger.error('Error in admin user DELETE:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get usage logs
router.get('/usage-logs', [
  logUserActivity('view', 'usage_logs'),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('user_id').optional().isInt({ min: 1 }),
  query('action').optional().isString(),
  query('start_date').optional().isISO8601().withMessage('Invalid start date format'),
  query('end_date').optional().isISO8601().withMessage('Invalid end date format')
], (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { page = 1, limit = 50, user_id, action, start_date, end_date } = req.query;
    const offset = (page - 1) * limit;
    const db = getDatabase();

    let whereClause = 'WHERE 1=1';
    let params = [];

    if (user_id) {
      whereClause += ' AND ul.user_id = ?';
      params.push(user_id);
    }

    if (action) {
      whereClause += ' AND ul.action = ?';
      params.push(action);
    }

    if (start_date) {
      whereClause += ' AND ul.timestamp >= ?';
      params.push(start_date);
    }

    if (end_date) {
      whereClause += ' AND ul.timestamp <= ?';
      params.push(end_date);
    }

    // Get total count
    db.get(`SELECT COUNT(*) as total FROM usage_logs ul ${whereClause}`, params, (err, countResult) => {
      if (err) {
        logger.error('Error counting usage logs:', err);
        return res.status(500).json({ error: 'Internal server error' });
      }

      // Get usage logs with pagination
      const query = `
        SELECT 
          ul.*,
          u.username as user_username
        FROM usage_logs ul
        LEFT JOIN users u ON ul.user_id = u.id
        ${whereClause}
        ORDER BY ul.timestamp DESC
        LIMIT ? OFFSET ?
      `;

      db.all(query, [...params, limit, offset], (err, logs) => {
        if (err) {
          logger.error('Error fetching usage logs:', err);
          return res.status(500).json({ error: 'Internal server error' });
        }

        res.json({
          logs,
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
    logger.error('Error in admin usage logs GET:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get system statistics
router.get('/system-stats', [
  logUserActivity('view', 'system_stats')
], (req, res) => {
  try {
    const db = getDatabase();
    
    const queries = {
      totalUsers: 'SELECT COUNT(*) as count FROM users',
      activeUsers: 'SELECT COUNT(*) as count FROM users WHERE is_active = 1',
      totalRecruits: 'SELECT COUNT(*) as count FROM potential_recruits',
      totalCadre: 'SELECT COUNT(*) as count FROM cadre',
      totalContacts: 'SELECT COUNT(*) as count FROM university_contacts',
      totalEvents: 'SELECT COUNT(*) as count FROM recruitment_events',
      recentLogins: 'SELECT COUNT(*) as count FROM users WHERE last_login >= date("now", "-7 days")',
      totalLogs: 'SELECT COUNT(*) as count FROM usage_logs',
      recentLogs: 'SELECT COUNT(*) as count FROM usage_logs WHERE timestamp >= date("now", "-24 hours")'
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
    logger.error('Error in admin system stats:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router; 