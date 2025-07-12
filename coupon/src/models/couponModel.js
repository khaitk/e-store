const mongoose = require('mongoose');

const couponSchema = new mongoose.Schema({
  code: {
    type: String,
    required: [true, 'Coupon code is required'],
    unique: true,
    trim: true,
    uppercase: true
  },
  type: {
    type: String,
    required: [true, 'Coupon type is required'],
    enum: ['percentage', 'fixed_amount', 'free_shipping']
  },
  value: {
    type: Number,
    required: [true, 'Coupon value is required'],
    min: [0, 'Value cannot be negative']
  },
  minPurchase: {
    type: Number,
    default: 0,
    min: [0, 'Minimum purchase cannot be negative']
  },
  maxDiscount: {
    type: Number,
    default: null
  },
  startDate: {
    type: Date,
    default: Date.now
  },
  endDate: {
    type: Date,
    default: null
  },
  usageLimit: {
    type: Number,
    default: null
  },
  usageCount: {
    type: Number,
    default: 0,
    min: [0, 'Usage count cannot be negative']
  },
  applicableProducts: {
    type: [String],
    default: []
  },
  applicableCategories: {
    type: [String],
    default: []
  },
  isActive: {
    type: Boolean,
    default: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

couponSchema.pre('findOneAndUpdate', function(next) {
  this.set({ updatedAt: new Date() });
  next();
});

couponSchema.methods.isValid = function() {
  const now = new Date();
  
  if (!this.isActive) return false;
  
  if (this.startDate && this.startDate > now) return false;
  if (this.endDate && this.endDate < now) return false;
  
  if (this.usageLimit !== null && this.usageCount >= this.usageLimit) return false;
  
  return true;
};

couponSchema.methods.calculateDiscount = function(orderAmount, shippingCost = 0) {
  if (orderAmount < this.minPurchase) return 0;
  
  let discountAmount = 0;
  
  switch (this.type) {
    case 'percentage':
      discountAmount = orderAmount * (this.value / 100);
      if (this.maxDiscount !== null && discountAmount > this.maxDiscount) {
        discountAmount = this.maxDiscount;
      }
      break;
    case 'fixed_amount':
      discountAmount = this.value;
      break;
    case 'free_shipping':
      discountAmount = shippingCost;
      break;
  }
  
  return discountAmount;
};

const Coupon = mongoose.model('Coupon', couponSchema);

module.exports = Coupon;
