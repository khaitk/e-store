const Coupon = require('../models/couponModel');

exports.createCoupon = async (req, res) => {
  const coupon = await Coupon.create(req.body);
  res.status(201).json({
    success: true,
    data: coupon
  });
};

exports.getCoupon = async (req, res) => {
  const coupon = await Coupon.findOne({ code: req.params.code });
  
  if (!coupon) {
    return res.status(404).json({
      success: false,
      error: 'Coupon not found.'
    });
  }
  
  res.status(200).json({
    success: true,
    data: coupon
  });
};

exports.updateCoupon = async (req, res) => {
  const coupon = await Coupon.findOneAndUpdate(
    { code: req.params.code },
    req.body,
    { new: true, runValidators: true }
  );
  
  if (!coupon) {
    return res.status(404).json({
      success: false,
      error: 'Coupon not found.'
    });
  }
  
  res.status(200).json({
    success: true,
    data: coupon
  });
};

exports.deleteCoupon = async (req, res) => {
  const coupon = await Coupon.findOneAndDelete({ code: req.params.code });
  
  if (!coupon) {
    return res.status(404).json({
      success: false,
      error: 'Coupon not found.'
    });
  }
  
  res.status(204).json({
    success: true,
    data: null
  });
};

exports.validateCoupon = async (req, res) => {
  const { code } = req.body;
  
  const coupon = await Coupon.findOne({ code });
  
  if (!coupon) {
    return res.status(404).json({
      success: false,
      message: 'Coupon not found.',
      valid: false
    });
  }
  
  const isValid = coupon.isValid();
  
  res.status(200).json({
    success: true,
    message: isValid ? 'Coupon is valid.' : 'Coupon is not valid.',
    valid: isValid,
    data: isValid ? coupon : null
  });
};

exports.applyCoupon = async (req, res) => {
  const { code, orderAmount, products, shippingCost } = req.body;
  
  const coupon = await Coupon.findOne({ code });
  
  if (!coupon) {
    return res.status(404).json({
      success: false,
      error: 'Coupon not found.'
    });
  }
  
  if (!coupon.isValid()) {
    return res.status(400).json({
      success: false,
      error: 'Coupon is not valid.'
    });
  }
  
  if (orderAmount < coupon.minPurchase) {
    return res.status(400).json({
      success: false,
      error: `Order amount must be at least ${coupon.minPurchase}`
    });
  }
  
  const discountAmount = coupon.calculateDiscount(orderAmount, shippingCost);
  
  coupon.usageCount += 1;
  await coupon.save();
  
  res.status(200).json({
    success: true,
    data: {
      originalAmount: orderAmount,
      discountAmount: discountAmount,
      finalAmount: orderAmount - discountAmount,
      coupon: coupon
    }
  });
};

exports.cleanupExpiredCoupons = async (req, res) => {
  const currentDate = new Date();
  
  const result = await Coupon.updateMany(
    { 
      endDate: { $lt: currentDate },
      isActive: true
    },
    { isActive: false }
  );
  
  res.status(200).json({
    success: true,
    message: `Deactivated ${result.modifiedCount} expired coupons.`
  });
};
