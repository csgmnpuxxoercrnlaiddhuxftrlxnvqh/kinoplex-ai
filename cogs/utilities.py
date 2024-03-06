import discord
#from discord import app_commands
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #this is intended as a fallback incase slash commands get out of sync
    @commands.command(name = "sync", hidden = True)
    async def sync(self, ctx, arg = None): 
        if ctx.author.id in self.bot.owner_ids or self.bot.bot_operators:
            print(f"Sync command issued by {ctx.author}")            
            if arg == "global":
                await self.bot.tree.sync()
                await ctx.send("Global command tree sync initiated, may take up to an hour")
            else:
                await self.bot.tree.sync(guild = ctx.guild)
                await ctx.send('Command tree synced.') 

async def setup(bot):
    await bot.add_cog(Utilities(bot),  guild = discord.Object(id = bot.guild_id))