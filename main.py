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

# Constants (replace these with your actual IDs)
GUILD_ID = 1385546298744373320
INFRACTIONS_CHANNEL_ID = 1395149042677186670
LAPD_ROLE_ID = 1395320865469759548
MASS_SHIFT_CHANNEL_ID = 1395372051988086894
PROMOTION_LOG_CHANNEL_ID = 1385555305475215440

# On ready event with guild command sync
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"🔄 Synced {len(synced)} slash commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# Log Infraction Command
@bot.tree.command(name="log_infraction", description="Log an officer infraction", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    officer="Select the officer",
    reason="Reason for the infraction",
    proof="Proof link or message (optional)",
    punishment="Punishment for the officer"
)
@app_commands.choices(punishment=[
    app_commands.Choice(name="Verbal Warning", value="Verbal Warning"),
    app_commands.Choice(name="Written Warning", value="Written Warning"),
    app_commands.Choice(name="Suspension", value="Suspension"),
    app_commands.Choice(name="Termination", value="Termination"),
    app_commands.Choice(name="None", value="None"),
])
async def log_infraction(interaction: discord.Interaction, officer: discord.Member, reason: str, proof: str = "None", punishment: app_commands.Choice[str] = None):
    embed = discord.Embed(title="🚨 Officer Infraction", color=discord.Color.red())
    embed.add_field(name="Officer", value=officer.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Proof", value=proof, inline=False)
    embed.add_field(name="Punishment", value=punishment.value if punishment else "None", inline=False)
    embed.set_footer(text=f"Issued by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    channel = bot.get_channel(INFRACTIONS_CHANNEL_ID)
    if channel:
        await channel.send(content=officer.mention, embed=embed)
        await interaction.response.send_message(f"Infraction logged for {officer.mention} in {channel.mention}.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Infractions channel not found.", ephemeral=True)

# Mass Shift Command
@bot.tree.command(name="mass_shift", description="Announce a mass shift", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    reason="Reason for the mass shift",
    promotional="Is this a promotional shift?",
    cohost="Select a co-host or type N/A"
)
@app_commands.choices(promotional=[
    app_commands.Choice(name="Yes", value="Yes"),
    app_commands.Choice(name="No", value="No"),
])
async def mass_shift(interaction: discord.Interaction, reason: str, promotional: app_commands.Choice[str], cohost: str):
    guild = bot.get_guild(GUILD_ID)
    lapd_role = guild.get_role(LAPD_ROLE_ID)
    channel = bot.get_channel(MASS_SHIFT_CHANNEL_ID)

    if not lapd_role or not channel:
        await interaction.response.send_message("❌ Required channel or role not found.", ephemeral=True)
        return

    cohost_member = None
    if cohost.lower() != "n/a":
        cohost_member = discord.utils.find(lambda m: m.name.lower() == cohost.lower() or str(m.id) == cohost, guild.members)

    embed = discord.Embed(title="📢 Mass Shift Announcement", color=discord.Color.blue())
    embed.add_field(name="LAPD Role", value=lapd_role.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Promotional", value=promotional.value, inline=False)
    embed.add_field(name="Co-Host", value=cohost_member.mention if cohost_member else "N/A", inline=False)
    embed.set_footer(text=f"Host: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    await channel.send(embed=embed)
    await interaction.response.send_message(f"Mass shift posted in {channel.mention}.", ephemeral=True)

# Promote Command
@bot.tree.command(name="promote", description="Promote an officer", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    officer="Select the officer",
    old_rank="Officer's current rank",
    new_rank="Officer's new rank",
    notes="Additional notes (optional)"
)
async def promote(interaction: discord.Interaction, officer: discord.Member, old_rank: discord.Role, new_rank: discord.Role, notes: str = "None"):
    if old_rank in officer.roles:
        await officer.remove_roles(old_rank, reason=f"Promoted by {interaction.user}")
    await officer.add_roles(new_rank, reason=f"Promoted by {interaction.user}")

    embed = discord.Embed(title="📈 Promotion Logged", color=discord.Color.green(), timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Officer", value=officer.mention, inline=False)
    embed.add_field(name="Old Rank", value=old_rank.mention, inline=True)
    embed.add_field(name="New Rank", value=new_rank.mention, inline=True)
    embed.add_field(name="Notes", value=notes, inline=False)
    embed.set_footer(text=f"Promoted by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    channel = bot.get_channel(PROMOTION_LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message(f"{officer.mention} promoted.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Promotion log channel not found.", ephemeral=True)

# Demote Command
@bot.tree.command(name="demote", description="Demote an officer", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    officer="Select the officer",
    old_rank="Officer's current rank",
    new_rank="Officer's new rank",
    notes="Additional notes (optional)"
)
async def demote(interaction: discord.Interaction, officer: discord.Member, old_rank: discord.Role, new_rank: discord.Role, notes: str = "None"):
    if old_rank in officer.roles:
        await officer.remove_roles(old_rank, reason=f"Demoted by {interaction.user}")
    await officer.add_roles(new_rank, reason=f"Demoted by {interaction.user}")

    embed = discord.Embed(title="📉 Demotion Logged", color=discord.Color.orange(), timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Officer", value=officer.mention, inline=False)
    embed.add_field(name="Old Rank", value=old_rank.mention, inline=True)
    embed.add_field(name="New Rank", value=new_rank.mention, inline=True)
    embed.add_field(name="Notes", value=notes, inline=False)
    embed.set_footer(text=f"Demoted by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    channel = bot.get_channel(PROMOTION_LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message(f"{officer.mention} demoted.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Promotion log channel not found.", ephemeral=True)

# Weather Command
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

    except Exception:
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
