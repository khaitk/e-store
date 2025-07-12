const express = require('express');
const router = express.Router();
const couponController = require('../controllers/couponController');

router.post('/', couponController.createCoupon);

router.get('/:code', couponController.getCoupon);

router.put('/:code', couponController.updateCoupon);

router.delete('/:code', couponController.deleteCoupon);

router.post('/validate', couponController.validateCoupon);

router.post('/apply', couponController.applyCoupon);

router.post('/cleanup', couponController.cleanupExpiredCoupons);

module.exports = router;
