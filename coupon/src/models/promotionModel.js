const mongoose = require('mongoose');

const promotionSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Promotion name is required'],
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  type: {
    type: String,
    required: [true, 'Promotion type is required'],
    enum: ['sale', 'bundle', 'bogo']
  },
  startDate: {
    type: Date,
    default: Date.now
  },
  endDate: {
    type: Date,
    default: null
  },
  discountValue: {
    type: Number,
    required: [true, 'Discount value is required'],
    min: [0, 'Discount value cannot be negative']
  },
  discountType: {
    type: String,
    required: [true, 'Discount type is required'],
    enum: ['percentage', 'fixed_amount']
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

promotionSchema.pre('findOneAndUpdate', function(next) {
  this.set({ updatedAt: new Date() });
  next();
});

promotionSchema.methods.isActive = function() {
  const now = new Date();
  
  if (!this.isActive) return false;
  
  if (this.startDate && this.startDate > now) return false;
  if (this.endDate && this.endDate < now) return false;
  
  return true;
};

const Promotion = mongoose.model('Promotion', promotionSchema);

module.exports = Promotion;
