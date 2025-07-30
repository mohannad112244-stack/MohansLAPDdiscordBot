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

        if self.bot.user in message.mentions or \
           (message.reference and message.reference.resolved and message.reference.resolved.author == self.bot.user):

            content_lower = message.content.lower()

            # Lots of keyword triggers and their replies
            responses = {
                "besties forever": "Absolutely, partners in crime! 👮‍♂️❤️",
                "test": "Testing, 1, 2, 3... Bot is online and ready!",
                "how are you": "I'm good, Officer! Always ready to assist you.",
                "hi": "Hey there! How can I help you today?",
                "hello": "Hello, Officer! What’s up?",
                "good morning": "Good morning! Hope you have a safe shift.",
                "good night": "Good night! Stay safe out there.",
                "thank you": "Anytime! Glad to help.",
                "thanks": "You're welcome, Officer!",
                "bye": "See you later, Officer! Stay safe.",
                "what's up": "Just keeping the city safe. What about you?",
                "help": "I'm here! What do you need assistance with?",
                "who are you": "I'm your trusty LAPD bot, here to assist with anything you need!",
                "joke": "Why did the police officer go to the bakery? Because he wanted a *doughnut* break! 🍩",
                "weather": "I don’t have weather updates yet, but stay prepared for anything!",
                "good job": "Thank you! You're doing great too.",
                "lol": "😄 Glad to see you’re enjoying yourself!",
                "congrats": "Congratulations! Keep up the great work.",
                "sorry": "No worries, Officer. We all make mistakes.",
                "ok": "Roger that!",
            }

            for trigger, reply in responses.items():
                if trigger in content_lower:
                    await message.channel.send(reply)
                    return

            # No keyword matched - fallback to OpenAI
            prompt = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
            if not prompt:
                await message.channel.send("Yes, Officer? How can I assist?")
                return

            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.7,
                )
                answer = response.choices[0].message.content.strip()
                await message.channel.send(answer)
            except Exception as e:
                print(f"OpenAI API error: {e}")
                await message.channel.send("Sorry, I can't process that right now.")

async def setup(bot):
    await bot.add_cog(LapdAI(bot))
