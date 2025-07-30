import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
from datetime import datetime, timezone

load_dotenv()  # Load local .env for dev; Railway overrides env vars automatically

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ BOT_TOKEN missing! Set it in your environment variables.")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1385546298744373320
INFRACTIONS_CHANNEL_ID = 1395149042677186670
LAPD_ROLE_ID = 1395320865469759548
MASS_SHIFT_CHANNEL_ID = 1395372051988086894
PROMOTION_LOG_CHANNEL_ID = 1385555305475215440

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"🔄 Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

@bot.event
async def setup_hook():
    # Load AI cog
    await bot.load_extension("lapd_ai")

# Your existing slash commands (log_infraction, mass_shift, promote, demote)
# Paste your existing commands here (from your original main.py) exactly as you had them,
# or I can help re-add them if you want.

keep_alive()
bot.run(TOKEN)
