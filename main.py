import discord
from aiosqlite import connect
from discord import app_commands


class MyClient(discord.Client):
    
    async def setup_hook(self):
        self.db = await connect("main.db")
    
    async def on_ready(self):
        print("Bot start")
        await self.db.execute("CREATE TABLE IF NOT EXISTS level(user BIGINT, level BIGINT, exp BIGINT)")
        
    async def send_level(self, message, level):
        await message.channel.send("{}さんあなたは{}ランクになりました".format(message.author.mention, level))
        
    async def level_up_check(self, message, data):
        user, level, exp = data
        if exp =< level * 3:
            level += 1
            await self.db.execute("UPDATE level SET level=?, exp=? WHERE=?", (level, exp, user))
            await self.send_level(message, level)
        
    async def on_message(self, message):
        cursor = await self.db.execute("SELECT * FROM level WHERE user=?", (message.author.id,))
        data = await cursor.fetchone()
        
        if data is not None:
            user, level, exp = data
            exp += 1
            await self.level_up_check(message, data)
        else:
            await self.db.execute("INSERT INTO level VALUES(?, ?, ?)", (message.author.id, 1, 1))
            await self.send_level(message, 1)
            
class Level_Tree(app_commands.Group):
    def __init__(self):
        super().__init__(name="level", description="level group command")
    
    @app_commands.command(description="check someone level")
    async def check(self, interaction, user: discord.User):
        pass
    
    
client = MyClient(intents=discord.Intents.all())


client.run()
