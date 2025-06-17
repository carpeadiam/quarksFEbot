const axios = require('axios');

module.exports = async (req, res) => {
  try {
    await axios.get(`${process.env.VERCEL_URL}/api/bot`);
    res.status(200).send('Bot pinged successfully');
  } catch (error) {
    res.status(500).send('Keepalive failed');
  }
};