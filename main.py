import discord
from aiosqlite import connect
from discord import app_commands
try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()


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
        if exp > level * 3:
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
    def __init__(self, client):
        super().__init__(name="level", description="level group command")
        self.db = client.db
        self.client = client
    
    @app_commands.command(description="check someone level")
    async def check(self, interaction, user: discord.User=None):
        data = await self.db.execute("SELECT * FROM level WHERE user=?", (user.id or interaction.author.id))
        if data is None:
            await interaction.response.send_message("そのユーザーは見つかりません")
        else:
            _, level, exp = data
            embed = discord.Embed(title="レベル情報")
            embed.add_field(name="レベル", value=level)
            await interaction.response.send_message(embed=embed)
            
    async def show_rank(self, user):
        ranks = []
        cursor = await self.db.execute("SELECT * FROM level")
        for user, level, _ in (await cursor.fetchall()):
            ranks.append((user, level))
        return sorted(ranks, key=lambda k: k[1])
            
    @app_commands.command(description="Check rank")
    async def rank(self, interaction):
        rank = "\n".join("{}. {}".format(i, self.client.get_user(data[1]).mention) for i, data in (await self.show_rank()))
        await interaction.response.send_message(embed=discord.Embed(title="ランキング", description=rank))
    
client = MyClient(intents=discord.Intents.all())


client.run()
