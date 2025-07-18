import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"  # Optional fallback

# Full intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Replace this with your actual server ID
GUILD_ID = 123456789012345678  # Example: 112233445566778899

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)  # Faster command sync
        print(f"🔄 Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

@bot.tree.command(name="infract", description="Log an officer infraction")
@app_commands.describe(
    officer="Officer name",
    reason="Infraction reason",
    proof="Link or message proof (optional)",
    punishment="What did the officer violate"
)
async def infract(interaction: discord.Interaction, officer: str, reason: str, proof: str = "None", punishment: str = "None"):
    print(f"📥 Slash command '/infract' invoked by {interaction.user}")
    try:
        embed = discord.Embed(title="🚨 Officer Infraction", color=discord.Color.red())
        embed.add_field(name="Officer", value=officer, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Proof", value=proof, inline=False)
        embed.add_field(name="Punishment", value=punishment, inline=False)
        embed.set_footer(text=f"Issued by {interaction.user}")
        await interaction.response.send_message(embed=embed)
        print("✅ Response sent.")
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
        except:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

# Start the bot
bot.run(TOKEN)
