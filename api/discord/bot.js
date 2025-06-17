const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');

const client = new Client({ 
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

// Verification command
client.on('messageCreate', async message => {
  if (message.author.bot) return;
  
  if (message.content.startsWith('!verify')) {
    const code = message.content.split(' ')[1];
    if (!code) return message.reply('❌ Please provide a verification code');
    
    try {
      const response = await axios.post(
        'https://thecodeworks.in/quarksfinance/api/discord/verify', 
        {
          code,
          discord_user_id: message.author.id
        },
        { timeout: 5000 }
      );
      
      message.reply(response.status === 200 
        ? '✅ Account linked successfully!' 
        : `❌ Error: ${response.data?.error || 'Verification failed'}`);
    } catch (error) {
      message.reply('⚠️ Server error - try again later');
      console.error('Verification error:', error);
    }
  }
});

// Vercel handler
module.exports = async (req, res) => {
  if (!client.isReady()) {
    await client.login(process.env.DISCORD_TOKEN);
    console.log(`Logged in as ${client.user.tag}`);
  }
  res.status(200).send('Bot is active');
};

