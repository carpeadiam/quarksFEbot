const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');

const client = new Client({ 
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages
  ]
});

// Verification command
client.on('messageCreate', async message => {
  if (!message.content.startsWith('!verify')) return;
  
  const code = message.content.split(' ')[1];
  if (!code) return message.reply('❌ Missing verification code');

  try {
    const response = await axios.post(
      'https://thecodeworks.in/quarksfinance/api/discord/verify',
      {
        code,
        discord_user_id: message.author.id
      },
      { timeout: 5000 }
    );
    message.reply(response.data.success ? '✅ Verified!' : '❌ Failed');
  } catch (error) {
    message.reply('⚠️ Service unavailable');
  }
});

module.exports = async (req, res) => {
  if (!client.isReady()) {
    await client.login(process.env.DISCORD_TOKEN);
    console.log(`Logged in as ${client.user.tag}`);
  }
  res.status(200).json({ status: 'active' });
};