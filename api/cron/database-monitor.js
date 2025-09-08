/**
 * Vercel Cron Job for Database Monitoring
 * Runs every 5 minutes to check database health and send alerts
 */

const { spawn } = require('child_process');
const { promisify } = require('util');
const { exec } = require('child_process');

const execAsync = promisify(exec);

module.exports = async function handler(req, res) {
  try {
    console.log('Database monitoring cron job started:', new Date().toISOString());

    // Run the Python database monitoring script
    const { stdout, stderr } = await execAsync('python database_monitor.py --cron-check');

    if (stderr) {
      console.error('Database monitoring stderr:', stderr);
    }

    console.log('Database monitoring output:', stdout);

    // Return success response
    res.status(200).json({
      success: true,
      timestamp: new Date().toISOString(),
      message: 'Database monitoring check completed',
      output: stdout
    });

  } catch (error) {
    console.error('Database monitoring error:', error);

    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
}

