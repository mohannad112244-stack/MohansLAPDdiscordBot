import discord
from discord import app_commands
from discord.ext import commands
import os
from keep_alive import keep_alive  # if you use this
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = 1385546298744373320  # your guild ID

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Logged in as {bot.user}")
    print(f"🔄 Synced commands to guild {GUILD_ID}")

@bot.tree.command(name="infract", description="Log an infraction", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(officer="Select the officer")
async def infract(interaction: discord.Interaction, officer: discord.Member):
    await interaction.response.send_message(f"Infraction logged for: {officer.display_name}", ephemeral=True)

keep_alive()  # if you use this
bot.run(TOKEN)
