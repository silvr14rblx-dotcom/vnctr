import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio

# Configuration
TOKEN = os.getenv("DISCORD_TOKEN")  # Load from environment variable for security
Target_Channel_ID = None # Optional: Set this if you only want it to work in a specific text channel

# Setup Bot with Intents (Required for checking Voice and Activities)
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.presences = True  # Required to see what game you are playing
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author.bot:
        return

    # Check if the user is in a Voice Channel
    if not message.author.voice or not message.author.voice.channel:
        return

    # Check if the user is playing a game (Steam/Rich Presence)
    is_playing = False
    if message.author.activities:
        for activity in message.author.activities:
            if activity.type == discord.ActivityType.playing:
                is_playing = True
                print(f"User {message.author} is playing: {activity.name}")
                break
    
    # Logic: If user is in VC AND playing a game, read the message
    if is_playing:
        vc_channel = message.author.voice.channel
        
        # Connect to Voice Client
        if message.guild.voice_client is None:
            vc = await vc_channel.connect()
        else:
            vc = message.guild.voice_client
            # Move if the bot is in a different channel
            if vc.channel.id != vc_channel.id:
                await vc.move_to(vc_channel)

        # Generate TTS Audio
        # We use gTTS (Google Text-to-Speech) to save a temporary MP3
        try:
            tts = gTTS(text=message.content, lang='en')
            filename = f"tts_{message.id}.mp3"
            tts.save(filename)

            # Play the Audio
            # We use FFmpegPCMAudio - Requires ffmpeg installed on the host
            if not vc.is_playing():
                vc.play(discord.FFmpegPCMAudio(filename), after=lambda e: clean_up(filename))
            else:
                # If already talking, maybe queue it (simple version: just skip or wait)
                pass 
                
        except Exception as e:
            print(f"Error generating TTS: {e}")

    await bot.process_commands(message)

def clean_up(filename):
    """Deletes the MP3 file after playing to save space."""
    if os.path.exists(filename):
        os.remove(filename)

bot.run(TOKEN)