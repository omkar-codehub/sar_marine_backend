require('dotenv').config();
const express = require('express');
const cors = require('cors');
const imageRoutes = require('./routes/imageRoutes');
const dziRoutes = require('./routes/dziRoutes');
const detectionRoutes = require('./routes/detectionRoutes');
const path = require('path');


const app = express();
const PORT = process.env.PORT || 3000;
app.use(cors());

// Middleware to parse JSON bodies
app.use(express.json());
app.use(express.urlencoded({ extended: true }));


// Serve oil spill DZI tiles
app.use('/tiles/oilspill', express.static(path.join(__dirname, '../shared/tiles/oilspill')));

// Serve ship detection DZI tiles
app.use('/tiles/ship', express.static(path.join(__dirname, '../shared/tiles/ship')));


app.use('/api/images', imageRoutes);
app.use('/api/dzi', dziRoutes);
// app.use('/api/detect', detectionRoutes);

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});