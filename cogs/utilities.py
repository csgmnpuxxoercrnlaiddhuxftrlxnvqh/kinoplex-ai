import discord
#from discord import app_commands
from discord.ext import commands
import traceback


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "sync", hidden = True)
    async def sync(self, ctx, arg = None): 
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:
            print(f"Sync command issued by {ctx.author}")            
            if arg == "global":
                await self.bot.tree.sync()
                await ctx.send("Global command tree sync initiated, may take up to an hour.")
            else:
                await self.bot.tree.sync(guild = ctx.guild)
                await ctx.send('Command tree synced.')

    @commands.command(name = "load_extension", aliases = ["l"], hidden = True)
    async def load_extension(self, ctx, extension_name: str):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:
            try:
                await self.bot.load_extension(f"cogs.{extension_name}")
            except Exception:
                await ctx.send(f"*Extension {extension_name} failed to load.*")
                traceback.print_exc()
            else:
                await ctx.send(f"Extension **{extension_name}** loaded.")

    @commands.command(name = "unload_extension", aliases = ["u"], hidden = True)
    async def unload_extension(self, ctx, extension_name: str):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:
            if extension_name == "utilities":
                await ctx.send(f"*The {extension_name} extension cannot be unloaded.*")
            else:
                await self.bot.unload_extension(f"cogs.{extension_name}")
                await ctx.send(f"Extension **{extension_name}** unloaded.")

    @commands.command(name = "reload_extension", aliases = ["r"], hidden = True)
    async def reload_extension(self, ctx, extension_name: str):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:
            try:    
                await self.bot.reload_extension(f"cogs.{extension_name}")
                await ctx.send(f"Extension **{extension_name}** reloaded.")
            except Exception:
                await ctx.send(f"*Extension {extension_name} failed to load.*")
                traceback.print_exc()
    
    @commands.command(name = "reload_all", aliases = ["ra"], hidden = True)
    async def reload_all(self, ctx):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:
            for extension in self.bot.start_extensions:
                if extension != "utilities":
                    try:
                        await self.bot.reload_extension(f"cogs.{extension}")
                        print(f"Extension **{extension}** reloaded")
                    except Exception:
                        await ctx.send(f"*Extension {extension} failed to load.*")
                        traceback.print_exc()

    @commands.command(name="nuke", hidden = True)
    async def nuke(self,ctx, num_messages:int=5):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:
            count = 0
            async for message in ctx.history(limit=200):
                if message.author.id == self.bot.user.id:
                    count += 1
                    await message.delete()
                if count == num_messages or count > 50: # limit just in case
                    break

async def setup(bot):
    await bot.add_cog(Utilities(bot),  guild = discord.Object(id = bot.guild_id))
