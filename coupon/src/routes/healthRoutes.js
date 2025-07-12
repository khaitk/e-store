const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');

/**
 * Health check endpoint for Coupon Service
 * 
 * Checks:
 * - API is running
 * - Database connection is working
 */
router.get('/health', async (req, res) => {
  const healthStatus = {
    status: 'healthy',
    service: 'coupon-service',
    checks: {
      api: 'up',
      database: 'unknown'
    }
  };
  
  // Check database connection
  if (mongoose.connection.readyState === 1) {
    healthStatus.checks.database = 'connected';
  } else {
    healthStatus.status = 'unhealthy';
    healthStatus.checks.database = `error: MongoDB connection state: ${mongoose.connection.readyState}`;
  }
  
  // Return appropriate status code based on health
  const statusCode = healthStatus.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(healthStatus);
});

module.exports = router;
