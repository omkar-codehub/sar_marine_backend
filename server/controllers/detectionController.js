const axios = require('axios');
const PYTHON_API_BASE = process.env.PYTHON_API_BASE || 'http://localhost:8000';

const allowedTypes = ['ship', 'oilspill'];

exports.runDetection = async (req, res) => {
  const { type, imageId } = req.params;

  if (!type || !allowedTypes.includes(type)) {
    return res.status(400).json({ error: 'Invalid type. Use "ship" or "oilspill".' });
  }

  if (!imageId) {
    return res.status(400).json({ error: 'Image ID required' });
  }

  try {
    // Call Python backend: /detect/{type}/{imageId}
    const response = await axios.post(`${PYTHON_API_BASE}/detect/dzi/${type}/${imageId}`);

    return res.status(200).json({
      message: `${type === 'ship' ? 'Ship' : 'Oil spill'} detection completed`,
      data: response.data
    });
  } catch (error) {
    console.error(`${type} detection error:`, error.message || error);
    return res.status(500).json({ error: `${type} detection failed` });
  }
};
