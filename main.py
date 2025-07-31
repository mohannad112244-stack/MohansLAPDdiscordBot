import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
from dotenv import load_dotenv
from keep_alive import keep_alive
from datetime import datetime, timezone

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = 1385546298744373320

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# On ready event
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"🔄 Synced {len(synced)} slash commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# Existing slash commands

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

    channel = bot.get_channel(1395149042677186670)  # INFRACTIONS_CHANNEL_ID
    if channel:
        await channel.send(content=officer.mention, embed=embed)
        await interaction.response.send_message(f"Infraction logged for {officer.mention} in {channel.mention}.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Infractions channel not found.", ephemeral=True)

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
    lapd_role = guild.get_role(1395320865469759548)  # LAPD_ROLE_ID
    channel = bot.get_channel(1395372051988086894)  # MASS_SHIFT_CHANNEL_ID

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

    channel = bot.get_channel(1385555305475215440)  # PROMOTION_LOG_CHANNEL_ID
    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message(f"{officer.mention} promoted.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Promotion log channel not found.", ephemeral=True)

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

    channel = bot.get_channel(1385555305475215440)  # PROMOTION_LOG_CHANNEL_ID
    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message(f"{officer.mention} demoted.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Promotion log channel not found.", ephemeral=True)

# New /weather command
@bot.tree.command(name="weather", description="Get current weather for a city", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(city="City name to get weather for")
async def weather(interaction: discord.Interaction, city: str):
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        await interaction.response.send_message("❌ Weather API key not configured.", ephemeral=True)
        return

    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    try:
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            await interaction.response.send_message(f"❌ Error: {data['error']['message']}", ephemeral=True)
            return

        current = data["current"]
        location = data["location"]

        weather_msg = (
            f"🌤️ **Weather for {location['name']}, {location['region'] or location['country']}**\n"
            f"Condition: {current['condition']['text']}\n"
            f"Temperature: {current['temp_c']}°C ({current['temp_f']}°F)\n"
            f"Feels Like: {current['feelslike_c']}°C\n"
            f"Humidity: {current['humidity']}%\n"
            f"Wind: {current['wind_kph']} kph"
        )
        await interaction.response.send_message(weather_msg)
    except Exception:
        await interaction.response.send_message("❌ Failed to fetch weather data.", ephemeral=True)

# Auto-replies to chat messages
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
    }

    for key, response in responses.items():
        if key in content:
            await message.channel.send(response)
            return

    await bot.process_commands(message)

# Keep bot alive & run
keep_alive()
bot.run(TOKEN)
