export default async (req, res) => {
  try {
    await fetch(`${process.env.VERCEL_URL}/api/discord/bot`);
    res.status(200).send('Keepalive triggered');
  } catch (error) {
    res.status(500).send('Keepalive failed');
  }
};