import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print("Bot start")
