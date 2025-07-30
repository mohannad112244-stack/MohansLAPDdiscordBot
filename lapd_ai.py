import discord
from discord.ext import commands
import os
import openai

class LapdAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        openai.api_key = os.getenv("OPENAI_API_KEY")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions or (message.reference and message.reference.resolved.author == self.bot.user):
            prompt = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

            if not prompt:
                await message.channel.send("Yes, Officer? How can I assist?")
                return

            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=150,
                    temperature=0.7,
                )
                answer = response.choices[0].text.strip()
                await message.channel.send(answer)
            except Exception:
                await message.channel.send("Sorry, I can't process that right now.")

def setup(bot):
    bot.add_cog(LapdAI(bot))
