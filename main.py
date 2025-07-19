import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
from datetime import datetime, timezone

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1385546298744373320
INFRACTIONS_CHANNEL_ID = 1395149042677186670
LAPD_ROLE_ID = 1395320865469759548
MASS_SHIFT_CHANNEL_ID = 1395372051988086894
PROMOTION_LOG_CHANNEL_ID = 1385555305475215440  # where promote/demote logs go

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"🔄 Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

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
    print(f"📥 /log_infraction invoked by {interaction.user}")

    embed = discord.Embed(title="🚨 Officer Infraction", color=discord.Color.red())
    embed.add_field(name="Officer", value=officer.mention, inline=False)  # mention for ping
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Proof", value=proof, inline=False)
    embed.add_field(name="Punishment", value=punishment.value if punishment else "None", inline=False)
    embed.set_footer(text=f"Issued by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    infractions_channel = bot.get_channel(INFRACTIONS_CHANNEL_ID)
    if infractions_channel:
        await infractions_channel.send(content=officer.mention, embed=embed)  # ping officer here
        await interaction.response.send_message(f"Infraction logged for {officer.mention} in {infractions_channel.mention}.", ephemeral=True)
        print("✅ Infraction logged and message sent.")
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
    print(f"📥 /mass_shift invoked by {interaction.user}")

    guild = bot.get_guild(GUILD_ID)
    lapd_role = guild.get_role(LAPD_ROLE_ID) if guild else None
    mass_shift_channel = bot.get_channel(MASS_SHIFT_CHANNEL_ID)

    if not lapd_role:
        await interaction.response.send_message("❌ LAPD role not found.", ephemeral=True)
        return

    if not mass_shift_channel:
        await interaction.response.send_message("❌ Mass shift channel not found.", ephemeral=True)
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

    await mass_shift_channel.send(embed=embed)
    await interaction.response.send_message(f"Mass shift announcement sent in {mass_shift_channel.mention}.", ephemeral=True)
    print("✅ Mass shift announcement sent.")


@bot.tree.command(name="promote", description="Promote an officer", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    officer="Select the officer",
    old_rank="Officer's current rank",
    new_rank="Officer's new rank",
    notes="Additional notes (optional)"
)
async def promote(interaction: discord.Interaction, officer: discord.Member, old_rank: discord.Role, new_rank: discord.Role, notes: str = "None"):
    print(f"📥 /promote invoked by {interaction.user}")

    # Remove old rank, add new rank silently
    if old_rank in officer.roles:
        await officer.remove_roles(old_rank, reason=f"Promoted by {interaction.user}")
    await officer.add_roles(new_rank, reason=f"Promoted by {interaction.user}")

    embed = discord.Embed(title="📈 Promotion Logged", color=discord.Color.green(), timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Officer", value=officer.mention, inline=False)  # mention to ping
    embed.add_field(name="Old Rank", value=old_rank.mention, inline=True)
    embed.add_field(name="New Rank", value=new_rank.mention, inline=True)
    embed.add_field(name="Notes", value=notes, inline=False)
    embed.set_footer(text=f"Promoted by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    promotion_log_channel = bot.get_channel(PROMOTION_LOG_CHANNEL_ID)
    if promotion_log_channel:
        await promotion_log_channel.send(embed=embed)
        await interaction.response.send_message(f"{officer.mention} promoted from {old_rank.name} to {new_rank.name}.", ephemeral=True)
        print("✅ Promotion logged and message sent.")
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
    print(f"📥 /demote invoked by {interaction.user}")

    # Remove old rank, add new rank silently
    if old_rank in officer.roles:
        await officer.remove_roles(old_rank, reason=f"Demoted by {interaction.user}")
    await officer.add_roles(new_rank, reason=f"Demoted by {interaction.user}")

    embed = discord.Embed(title="📉 Demotion Logged", color=discord.Color.orange(), timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Officer", value=officer.mention, inline=False)  # mention to ping
    embed.add_field(name="Old Rank", value=old_rank.mention, inline=True)
    embed.add_field(name="New Rank", value=new_rank.mention, inline=True)
    embed.add_field(name="Notes", value=notes, inline=False)
    embed.set_footer(text=f"Demoted by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    promotion_log_channel = bot.get_channel(PROMOTION_LOG_CHANNEL_ID)
    if promotion_log_channel:
        await promotion_log_channel.send(embed=embed)
        await interaction.response.send_message(f"{officer.mention} demoted from {old_rank.name} to {new_rank.name}.", ephemeral=True)
        print("✅ Demotion logged and message sent.")
    else:
        await interaction.response.send_message("❌ Promotion log channel not found.", ephemeral=True)


keep_alive()
bot.run(TOKEN)
