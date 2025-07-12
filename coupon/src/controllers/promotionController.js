const Promotion = require('../models/promotionModel');

exports.getActivePromotions = async (req, res) => {
  const currentDate = new Date();
  
  const promotions = await Promotion.find({
    isActive: true,
    startDate: { $lte: currentDate },
    $or: [
      { endDate: null },
      { endDate: { $gte: currentDate } }
    ]
  });
  
  res.status(200).json({
    success: true,
    count: promotions.length,
    data: promotions
  });
};

exports.createPromotion = async (req, res) => {
  const promotion = await Promotion.create(req.body);
  
  res.status(201).json({
    success: true,
    data: promotion
  });
};

exports.getPromotion = async (req, res) => {
  const promotion = await Promotion.findById(req.params.id);
  
  if (!promotion) {
    return res.status(404).json({
      success: false,
      error: 'Promotion not found'
    });
  }
  
  res.status(200).json({
    success: true,
    data: promotion
  });
};

exports.updatePromotion = async (req, res) => {
  const promotion = await Promotion.findByIdAndUpdate(
    req.params.id,
    req.body,
    { new: true, runValidators: true }
  );
  
  if (!promotion) {
    return res.status(404).json({
      success: false,
      error: 'Promotion not found'
    });
  }
  
  res.status(200).json({
    success: true,
    data: promotion
  });
};

exports.deletePromotion = async (req, res) => {
  const promotion = await Promotion.findByIdAndDelete(req.params.id);
  
  if (!promotion) {
    return res.status(404).json({
      success: false,
      error: 'Promotion not found'
    });
  }
  
  res.status(204).json({
    success: true,
    data: null
  });
};

exports.getPromotionsByProduct = async (req, res) => {
  const productId = req.params.productId;
  const currentDate = new Date();
  
  const promotions = await Promotion.find({
    isActive: true,
    startDate: { $lte: currentDate },
    $or: [
      { endDate: null },
      { endDate: { $gte: currentDate } }
    ],
    $or: [
      { applicableProducts: { $size: 0 } },
      { applicableProducts: productId }
    ]
  });
  
  res.status(200).json({
    success: true,
    count: promotions.length,
    data: promotions
  });
};

exports.getPromotionsByCategory = async (req, res) => {
  const categoryId = req.params.categoryId;
  const currentDate = new Date();
  
  const promotions = await Promotion.find({
    isActive: true,
    startDate: { $lte: currentDate },
    $or: [
      { endDate: null },
      { endDate: { $gte: currentDate } }
    ],
    $or: [
      { applicableCategories: { $size: 0 } },
      { applicableCategories: categoryId }
    ]
  });
  
  res.status(200).json({
    success: true,
    count: promotions.length,
    data: promotions
  });
};
