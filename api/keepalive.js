const fetch = require('node-fetch');

module.exports = async (req, res) => {
  await fetch(`${process.env.VERCEL_URL}/api/bot`);
  res.status(200).send('Pinged bot');
};