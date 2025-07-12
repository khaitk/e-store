require('dotenv').config();
require('express-async-errors');
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

const { connectDB } = require('./config/db');
const couponRoutes = require('./routes/couponRoutes');
const promotionRoutes = require('./routes/promotionRoutes');
const healthRoutes = require('./routes/healthRoutes');
const errorHandler = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 8002;

// Middleware
app.use(express.json());
app.use(cors());
app.use(helmet());
app.use(morgan('dev'));

// Routes
app.use('/api/coupons', couponRoutes);
app.use('/api/promotions', promotionRoutes);
app.use('/', healthRoutes);

// Root route
app.get('/', (req, res) => {
  res.json({ message: 'Welcome to Coupon Service' });
});

// Error handling middleware
app.use(errorHandler);

const start = async () => {
  try {
    await connectDB();
    app.listen(PORT, () => {
      console.log(`Coupon Service running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

start();
