import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive  # if you have this for uptime, else remove

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

# IDs
GUILD_ID = 1385546298744373320  # Your server ID here
INFRACTION_CHANNEL_ID = 1395149042677186670  # Your infraction channel ID here

# Intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"🔄 Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

@bot.tree.command(name="log infraction", description="Log an officer infraction", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    officer="Select the officer",
    reason="Reason for the infraction",
    proof="Proof link or message (optional)",
    punishment="Punishment given"
)
async def log_infraction(
    interaction: discord.Interaction,
    officer: discord.Member,
    reason: str,
    proof: str = "None",
    punishment: str = "None"
):
    embed = discord.Embed(title="🚨 Officer Infraction", color=discord.Color.red())
    embed.add_field(name="Officer", value=officer.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Proof", value=proof, inline=False)
    embed.add_field(name="Punishment", value=punishment, inline=False)
    embed.add_field(name="Signed by", value=interaction.user.name, inline=False)
    embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.display_avatar.url)

    channel = bot.get_channel(INFRACTION_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message("❌ Infraction channel not found.", ephemeral=True)
        return

    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Infraction logged for {officer.mention}.", ephemeral=True)

# Start keep_alive server if you have it
keep_alive()

bot.run(TOKEN)
