import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
from dotenv import load_dotenv
from keep_alive import keep_alive
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = 1385546298744373320

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Ready Event
@bot.event
async def on_ready():
    synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"🔄 Synced {len(synced)} slash commands to guild {GUILD_ID}")

# Slash Commands
@bot.tree.command(name="log_infraction", description="Logs an infraction", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="User to log", reason="Reason for infraction")
async def log_infraction(interaction: discord.Interaction, user: discord.Member, reason: str):
    await interaction.response.send_message(f"Logged infraction for {user.mention}: {reason}", ephemeral=True)

@bot.tree.command(name="mass_shift", description="Starts a mass shift", guild=discord.Object(id=GUILD_ID))
async def mass_shift(interaction: discord.Interaction):
    await interaction.response.send_message("@here A mass shift is starting! Please report to HQ.", ephemeral=False)

@bot.tree.command(name="promote", description="Promote a member", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="User to promote", new_rank="New rank for the user")
async def promote(interaction: discord.Interaction, user: discord.Member, new_rank: str):
    log_channel = bot.get_channel(1385555305475215440)
    await log_channel.send(f"✅ {user.mention} has been promoted to **{new_rank}** by {interaction.user.mention}")
    await interaction.response.send_message(f"Promoted {user.mention} to {new_rank}", ephemeral=True)

@bot.tree.command(name="demote", description="Demote a member", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="User to demote", new_rank="New rank for the user")
async def demote(interaction: discord.Interaction, user: discord.Member, new_rank: str):
    log_channel = bot.get_channel(1385555305475215440)
    await log_channel.send(f"⚠️ {user.mention} has been demoted to **{new_rank}** by {interaction.user.mention}")
    await interaction.response.send_message(f"Demoted {user.mention} to {new_rank}", ephemeral=True)

# Message Auto-Response & Weather
@bot.event
async def on_message(message):
    if message.author.bot:
        return

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
        "weather": None  # Special case handled below
    }

    for key, response in responses.items():
        if key in content:
            if key == "weather":
                weather_key = os.getenv("WEATHER_API_KEY")
                if not weather_key:
                    await message.channel.send("❌ Weather API key not configured.")
                    return

                try:
                    r = requests.get(f"http://api.weatherapi.com/v1/current.json?key={weather_key}&q=Los Angeles")
                    data = r.json()
                    temp = data["current"]["temp_c"]
                    condition = data["current"]["condition"]["text"]
                    humidity = data["current"]["humidity"]
                    wind_kph = data["current"]["wind_kph"]

                    weather_text = f"🌤️ **Los Angeles Weather:** {temp}°C, {condition}\n💨 Wind: {wind_kph} km/h | 💧 Humidity: {humidity}%"
                    await message.channel.send(weather_text)
                except Exception as e:
                    await message.channel.send("❌ Failed to fetch weather.")
                return
            else:
                await message.channel.send(response)
                return

    await bot.process_commands(message)

# Keep Alive + Run Bot
keep_alive()
bot.run(TOKEN)
