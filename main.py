import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive  # remove if you don't use it

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1385546298744373320  # Your guild/server ID here
INFRACTIONS_CHANNEL_ID = 1395149042677186670  # Channel ID to send infraction logs

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"🔄 Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

@bot.tree.command(
    name="log_infraction",  # NO spaces allowed here
    description="Log an officer infraction"
)
@app_commands.describe(
    officer="Select the officer",
    reason="Infraction reason",
    proof="Link or message proof (optional)",
    punishment="What did the officer violate"
)
@app_commands.guilds(discord.Object(id=GUILD_ID))
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
    embed.set_footer(
        text=f"Issued by {interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url
    )

    channel = bot.get_channel(INFRACTIONS_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message("❌ Infraction channel not found.", ephemeral=True)
        return

    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Infraction logged for {officer.mention}", ephemeral=True)

keep_alive()  # Remove if you don't use

bot.run(TOKEN)
