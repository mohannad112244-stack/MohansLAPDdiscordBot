import discord
from discord.ext import commands
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class LAPDAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        bot_user = self.bot.user
        bot_mentioned = bot_user in message.mentions
        replied_to_bot = False

        if message.reference:
            try:
                replied_msg = await message.channel.fetch_message(message.reference.message_id)
                if replied_msg.author == bot_user:
                    replied_to_bot = True
            except Exception:
                pass

        if bot_mentioned or replied_to_bot:
            content = message.content.replace(f"<@{bot_user.id}>", "").strip()
            if not content:
                content = "Hello!"

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=150,
                    temperature=0.7,
                )
                reply_text = response.choices[0].message.content.strip()
            except Exception:
                reply_text = "Sorry, I couldn't process that right now."

            await message.channel.send(reply_text)

def setup(bot):
    bot.add_cog(LAPDAI(bot))
