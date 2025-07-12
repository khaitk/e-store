const express = require('express');
const router = express.Router();
const promotionController = require('../controllers/promotionController');

router.get('/', promotionController.getActivePromotions);

router.post('/', promotionController.createPromotion);

router.get('/:id', promotionController.getPromotion);

router.put('/:id', promotionController.updatePromotion);

router.delete('/:id', promotionController.deletePromotion);

router.get('/product/:productId', promotionController.getPromotionsByProduct);

router.get('/category/:categoryId', promotionController.getPromotionsByCategory);

module.exports = router;
