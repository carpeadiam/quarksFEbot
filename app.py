import os
import discord
from discord.ext import commands
from discord import app_commands
import requests
from flask import Flask, request, jsonify
from threading import Thread

# Initialize
app = Flask(__name__)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


async def send_dm(user_id: int, message: str):
    try:
        user = await bot.fetch_user(user_id)
        if user:
            await user.send(message)
    except Exception as e:
        print(f"Error sending DM to {user_id}: {e}")



@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot is ready. Logged in as {bot.user}')
    print('Slash commands synced.')

@bot.tree.command(name="verify", description="Verify your Discord with a code")
@app_commands.describe(code="Your verification code")
async def verify(interaction: discord.Interaction, code: str):
    try:
        response = requests.post(
            'https://thecodeworks.in/quarksfinance/api/discord/verify',
            json={'code': code, 'discord_user_id': interaction.user.id},
            timeout=5
        )
        await interaction.response.send_message("✅ Verified!" if response.ok else "❌ Failed")
    except Exception as e:
        
        await interaction.response.send_message(f"⚠️ Error: {str(e)}")


@bot.tree.command(name="terminal", description="Execute a command through the terminal backend")
@app_commands.describe(command="The command you want to run")
async def terminal(interaction: discord.Interaction, command: str):
    await interaction.response.defer()  # Show "thinking..." message

    try:
        response = requests.post(
            'https://thecodeworks.in/quarksfinance/api/terminal_bot',
            json={
                'command': command,
                'discord_user_id': interaction.user.id
            },
            timeout=20
        )

        if response.ok:
            data = response.json()
            if data.get("success"):
                await interaction.followup.send(f"📤 **Output:**\n```\n{data['result']}\n```")
            else:
                await interaction.followup.send(f"⚠️ Error:\n```\n{data['result']}\n```")
        else:
            await interaction.followup.send("❌ Backend returned an error.")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Request failed:\n```\n{str(e)}\n```")



@bot.tree.command(name="fein", description="Bot joins your VC and plays Fein.mp3")
async def fein(interaction: discord.Interaction):
    await interaction.response.defer()

    if interaction.guild is None:
        await interaction.followup.send("❌ This command can only be used in a server.")
        return

    # Safely get the Member object
    member = interaction.guild.get_member(interaction.user.id)
    if not member or not member.voice or not member.voice.channel:
        await interaction.followup.send("❌ You must be in a voice channel.")
        return

    vc_channel = member.voice.channel

    try:
        # Connect to VC or move if already connected
        if interaction.guild.voice_client:
            voice_client = interaction.guild.voice_client
            await voice_client.move_to(vc_channel)
        else:
            voice_client = await vc_channel.connect()

        if voice_client.is_playing():
            await interaction.followup.send("⚠️ Already playing audio.")
            return

        # Play Fein.mp3
        audio_source = discord.FFmpegPCMAudio("Fein.mp3")

        def after_playback(error):
            coro = voice_client.disconnect()
            fut = discord.utils.run_coroutine_threadsafe(coro, bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error disconnecting: {e}")

        voice_client.play(audio_source, after=after_playback)
        await interaction.followup.send("🎶 Playing *Fein.mp3*! Leaving after playback.")

    except Exception as e:
        await interaction.followup.send(f"⚠️ Playback error:\n```\n{str(e)}\n```")


@bot.tree.command(name="feinleave", description="Disconnect the bot from the VC manually")
async def feinleave(interaction: discord.Interaction):
    await interaction.response.defer()

    if interaction.guild is None:
        await interaction.followup.send("❌ This command can only be used in a server.")
        return

    voice_client = interaction.guild.voice_client

    if not voice_client:
        await interaction.followup.send("⚠️ I'm not connected to any voice channel.")
        return

    try:
        await voice_client.disconnect()
        await interaction.followup.send("👋 Disconnected from voice channel.")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error disconnecting: {str(e)}")


@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_id = data.get("discord_user_id")
    message = data.get("message")

    if not user_id or not message:
        return {"error": "Missing 'discord_user_id' or 'message'"}, 400

    try:
        # Schedule the coroutine to run in the bot event loop
        bot.loop.create_task(send_dm(int(user_id), message))
        return {"success": True, "status": "Message scheduled"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/')
def home():
    return "Bot is alive", 200

def run_bot():
    bot.run("MTM4NDEzNTk1OTI1NTE5MTY3Mg.GbPgpw.qpOOIBNSMttXnBsRR9KpuebbVe9FgpgTP5IsXE")

if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
