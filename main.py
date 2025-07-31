import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
from datetime import datetime, timezone
import requests

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables!")

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Constants (replace these IDs with your actual server/channel/role IDs)
GUILD_ID = 1385546298744373320
INFRACTIONS_CHANNEL_ID = 1395149042677186670
LAPD_ROLE_ID = 1395320865469759548
MASS_SHIFT_CHANNEL_ID = 1395372051988086894
PROMOTION_LOG_CHANNEL_ID = 1385555305475215440

# On ready event with sync
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"🔄 Synced {len(synced)} slash commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# Your slash commands below (log_infraction, mass_shift, promote, demote)
# ... [Keep all your existing slash commands here unchanged] ...

# Example: Log Infraction command (keep your existing code for all commands)
# (Omitted here for brevity but keep as you had it)

# Weather slash command example (assumes you have WEATHER_API_KEY in .env)
@bot.tree.command(name="weather", description="Get the weather for Los Angeles", guild=discord.Object(id=GUILD_ID))
async def weather(interaction: discord.Interaction):
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    if not WEATHER_API_KEY:
        await interaction.response.send_message("❌ Weather API key not set.", ephemeral=True)
        return

    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q=Los Angeles"
    try:
        response = requests.get(url)
        data = response.json()
        location = data['location']['name']
        temp_c = data['current']['temp_c']
        condition = data['current']['condition']['text']
        humidity = data['current']['humidity']
        wind_kph = data['current']['wind_kph']

        embed = discord.Embed(title=f"Weather in {location}", color=discord.Color.blue())
        embed.add_field(name="Temperature", value=f"{temp_c} °C", inline=True)
        embed.add_field(name="Condition", value=condition, inline=True)
        embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="Wind Speed", value=f"{wind_kph} kph", inline=True)
        embed.set_footer(text="Powered by weatherapi.com")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message("❌ Failed to get weather data.", ephemeral=True)

# on_message event - replies only if bot is mentioned or replied to
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Only respond if bot is mentioned or message is a reply to the bot
    if bot.user in message.mentions or (message.reference and message.reference.resolved and message.reference.resolved.author == bot.user):
        content = message.content.lower()

        responses = {
            "hi": "Hey there!",
            "hello": "Hello 👋",
            "how are you": "I'm just a bot, but I'm doing great!",
            "besties forever": "💖 Besties forever!",
            "test": "Test received loud and clear!",
            "gm": "Good morning ☀️",
            "gn": "Good night 🌙",
            "sup": "Not much, what's up with you?",
            "yo": "Yo! 👋",
            "what's up": "All systems operational 🚓",
        }

        for key, response in responses.items():
            if key in content:
                await message.channel.send(response)
                break  # Only one reply per message

    await bot.process_commands(message)

# Load LapdAI Cog on startup
@bot.event
async def on_connect():
    await bot.load_extension("lapd_ai")

# Start keep_alive webserver and run bot
keep_alive()
bot.run(TOKEN)
