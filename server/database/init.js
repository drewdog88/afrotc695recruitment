const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bcrypt = require('bcryptjs');
const { logger } = require('../utils/logger');

const dbPath = process.env.DB_PATH || path.join(__dirname, 'afrotc695.db');
let db;

function initializeDatabase() {
  return new Promise((resolve, reject) => {
    db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        logger.error('Error opening database:', err);
        reject(err);
        return;
      }
      
      logger.info('Connected to SQLite database');
      createTables()
        .then(() => createDefaultAdmin())
        .then(() => resolve())
        .catch(reject);
    });
  });
}

function createTables() {
  return new Promise((resolve, reject) => {
    const tables = [
      // Users table for authentication
      `CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME,
        login_count INTEGER DEFAULT 0
      )`,
      
      // Potential recruits table
      `CREATE TABLE IF NOT EXISTS potential_recruits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        major TEXT,
        current_school TEXT NOT NULL,
        school_type TEXT CHECK(school_type IN ('high_school', 'college')) NOT NULL,
        high_school_graduation_year INTEGER,
        expected_college_graduation_year INTEGER,
        gpa REAL,
        sat_score INTEGER,
        act_score INTEGER,
        interests TEXT,
        notes TEXT,
        status TEXT DEFAULT 'prospective' CHECK(status IN ('prospective', 'contacted', 'interested', 'applied', 'enrolled', 'not_interested')),
        assigned_to INTEGER,
        created_by INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (assigned_to) REFERENCES users (id),
        FOREIGN KEY (created_by) REFERENCES users (id)
      )`,
      
      // Cadre table
      `CREATE TABLE IF NOT EXISTS cadre (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        major TEXT NOT NULL,
        graduation_year INTEGER NOT NULL,
        cadet_rank TEXT NOT NULL,
        hometown TEXT,
        officer_interest TEXT,
        is_enrolled BOOLEAN DEFAULT 1,
        unenrollment_reason TEXT,
        unenrollment_date DATE,
        gpa REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,
      
      // University contacts table
      `CREATE TABLE IF NOT EXISTS university_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        university_name TEXT NOT NULL,
        contact_name TEXT NOT NULL,
        contact_title TEXT,
        email TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        notes TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,
      
      // Recruitment events table
      `CREATE TABLE IF NOT EXISTS recruitment_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        event_date DATE NOT NULL,
        start_time TIME,
        end_time TIME,
        location TEXT,
        university_id INTEGER,
        event_type TEXT CHECK(event_type IN ('info_session', 'career_fair', 'campus_visit', 'other')) NOT NULL,
        status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'completed', 'cancelled')),
        attendees_count INTEGER DEFAULT 0,
        notes TEXT,
        created_by INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (university_id) REFERENCES university_contacts (id),
        FOREIGN KEY (created_by) REFERENCES users (id)
      )`,
      
      // Usage tracking table
      `CREATE TABLE IF NOT EXISTS usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        resource TEXT NOT NULL,
        ip_address TEXT,
        user_agent TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
      )`
    ];

    let completed = 0;
    const total = tables.length;

    tables.forEach((table, index) => {
      db.run(table, (err) => {
        if (err) {
          logger.error(`Error creating table ${index + 1}:`, err);
          reject(err);
          return;
        }
        
        completed++;
        if (completed === total) {
          logger.info('All tables created successfully');
          resolve();
        }
      });
    });
  });
}

function createDefaultAdmin() {
  return new Promise((resolve, reject) => {
    const defaultAdmin = {
      username: 'admin',
      email: 'admin@afrotc695.edu',
      password: 'admin123', // This should be changed immediately
      role: 'admin'
    };

    // Check if admin already exists
    db.get('SELECT id FROM users WHERE username = ?', [defaultAdmin.username], (err, row) => {
      if (err) {
        reject(err);
        return;
      }

      if (row) {
        logger.info('Default admin user already exists');
        resolve();
        return;
      }

      // Create default admin
      bcrypt.hash(defaultAdmin.password, 12).then(hash => {
        db.run(
          'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
          [defaultAdmin.username, defaultAdmin.email, hash, defaultAdmin.role],
          (err) => {
            if (err) {
              reject(err);
              return;
            }
            logger.info('Default admin user created');
            logger.warn('IMPORTANT: Change the default admin password immediately!');
            resolve();
          }
        );
      }).catch(reject);
    });
  });
}

function getDatabase() {
  return db;
}

function closeDatabase() {
  return new Promise((resolve, reject) => {
    if (db) {
      db.close((err) => {
        if (err) {
          reject(err);
          return;
        }
        logger.info('Database connection closed');
        resolve();
      });
    } else {
      resolve();
    }
  });
}

module.exports = {
  initializeDatabase,
  getDatabase,
  closeDatabase
}; 