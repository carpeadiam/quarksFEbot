const { Client, GatewayIntentBits, REST, Routes } = require('discord.js');
const axios = require('axios');

const client = new Client({ 
  intents: [GatewayIntentBits.Guilds] 
});

// Slash Command Setup
const commands = [
  {
    name: 'verify',
    description: 'Link your Quarks Finance account',
    options: [
      {
        name: 'code',
        description: 'Your verification code',
        type: 3, // STRING type
        required: true
      }
    ]
  }
];

// Register slash commands
async function registerCommands() {
  try {
    const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);
    await rest.put(
      Routes.applicationCommands(process.env.DISCORD_CLIENT_ID),
      { body: commands }
    );
    console.log('Slash commands registered!');
  } catch (error) {
    console.error('Command registration failed:', error);
  }
}

// Slash command handler
client.on('interactionCreate', async interaction => {
  if (!interaction.isCommand()) return;

  if (interaction.commandName === 'verify') {
    const code = interaction.options.getString('code');
    
    try {
      const response = await axios.post(
        'https://thecodeworks.in/quarksfinance/api/discord/verify',
        {
          code,
          discord_user_id: interaction.user.id
        }
      );
      
      await interaction.reply({ 
        content: response.data.success ? '✅ Account linked!' : '❌ Verification failed',
        ephemeral: true 
      });
    } catch (error) {
      await interaction.reply({
        content: '⚠️ Service error - try again later',
        ephemeral: true
      });
    }
  }
});

// Startup
client.login(process.env.DISCORD_TOKEN)
  .then(registerCommands)
  .catch(console.error);

// Vercel handler
module.exports = async (req, res) => {
  res.status(200).json({ 
    status: 'active',
    commands: commands.map(cmd => cmd.name)
  });
};