const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { getDatabase } = require('../database/init');
const { logger } = require('../utils/logger');

// Middleware to verify JWT token
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key', (err, user) => {
    if (err) {
      logger.warn(`Invalid token attempt: ${err.message}`);
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
}

// Middleware to check if user has admin role
function requireAdmin(req, res, next) {
  if (!req.user) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  if (req.user.role !== 'admin') {
    logger.warn(`Unauthorized admin access attempt by user: ${req.user.username}`);
    return res.status(403).json({ error: 'Admin privileges required' });
  }

  next();
}

// Middleware to check if user has specific role
function requireRole(role) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    if (req.user.role !== role && req.user.role !== 'admin') {
      logger.warn(`Unauthorized access attempt by user: ${req.user.username} for role: ${role}`);
      return res.status(403).json({ error: `Role '${role}' required` });
    }

    next();
  };
}

// Function to log user activity
function logActivity(userId, action, resource, req) {
  const db = getDatabase();
  const ipAddress = req.ip || req.connection.remoteAddress;
  const userAgent = req.get('User-Agent');

  db.run(
    'INSERT INTO usage_logs (user_id, action, resource, ip_address, user_agent) VALUES (?, ?, ?, ?, ?)',
    [userId, action, resource, ipAddress, userAgent],
    (err) => {
      if (err) {
        logger.error('Error logging activity:', err);
      }
    }
  );
}

// Middleware to log activity
function logUserActivity(action, resource) {
  return (req, res, next) => {
    if (req.user) {
      logActivity(req.user.id, action, resource, req);
    }
    next();
  };
}

module.exports = {
  authenticateToken,
  requireAdmin,
  requireRole,
  logActivity,
  logUserActivity
}; 