const express = require('express');
const router = express.Router();
const detectionController = require('../controllers/detectionController');

// Unified detection route by type
router.post('/:type/:imageId', detectionController.runDetection);

module.exports = router;
