import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

# Load token and set intents
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # MUST be True for member resolving

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1385546298744373320  # Your server ID as int

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    guild = discord.Object(id=GUILD_ID)
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"🔄 Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

@bot.tree.command(name="infract", description="Log an officer infraction")
@app_commands.describe(
    officer="Select an officer from the server",
    reason="Infraction reason",
    proof="Proof link or message (optional)",
    punishment="Punishment (optional)"
)
async def infract(interaction: discord.Interaction, officer: discord.Member, reason: str, proof: str = "None", punishment: str = "None"):
    try:
        embed = discord.Embed(title="🚨 Officer Infraction", color=discord.Color.red())
        embed.add_field(name="Officer", value=officer.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Proof", value=proof, inline=False)
        embed.add_field(name="Punishment", value=punishment, inline=False)
        embed.set_footer(text=f"Issued by {interaction.user}")

        await interaction.response.send_message(embed=embed)
        print(f"✅ Infraction logged for {officer} by {interaction.user}")
    except Exception as e:
        print(f"❌ Error in infract command: {e}")
        try:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
        except:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

# Start keep_alive server
keep_alive()

bot.run(TOKEN)
