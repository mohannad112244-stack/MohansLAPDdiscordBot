import discord
from discord import app_commands
from discord.ext import commands
import os
from keep_alive import keep_alive  # ✅ keeps bot alive (for Railway or Replit)
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=1385546298744373320)  # ✅ Your Guild ID

@bot.event
async def on_ready():
    await bot.tree.sync(guild=GUILD_ID)
    print(f"✅ Logged in as {bot.user}")
    print("🔁 Synced slash commands to guild.")

@bot.tree.command(name="infract", description="Log an infraction", guild=GUILD_ID)
@app_commands.describe(officer="Select the officer")
async def infract(interaction: discord.Interaction, officer: discord.Member):
    await interaction.response.send_message(f"📋 Infraction logged for {officer.display_name}", ephemeral=True)

# ✅ Keep bot alive (needed for Replit or Railway with UptimeRobot)
keep_alive()

# 🚀 Run the bot
bot.run(TOKEN)

