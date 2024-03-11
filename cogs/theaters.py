import discord
from discord import app_commands
from discord.ext import commands

class Theaters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod                                   #is this actually a static method?
    async def role_mod(self, user, emoji, side):
        if emoji not in self.bot.emojimap: return
        role = discord.utils.get(self.bot.guild.roles, id=self.bot.emojimap[emoji])
        if side == "add":
            print(f"User {user} reacted with {emoji}, adding role {role}")
            await user.add_roles(role)
        elif side == "remove":
            print(f"User {user} removed their {emoji} reaction, removing role {role}")
            await user.remove_roles(role)
    
    @commands.Cog.listener()  
    async def on_raw_reaction_add(self, payload):
        en = payload.emoji.name
        user = self.bot.guild.get_member(payload.user_id)
        if payload.message_id == self.bot.react_msg_theater:
            if payload.user_id in self.bot.owner_ids: 
                return
            await self.role_mod(self, user, en, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        en = payload.emoji.name
        user = self.bot.guild.get_member(payload.user_id)
        if payload.message_id == self.bot.react_msg_theater:
            if payload.user_id in self.bot.owner_ids: 
                return
            await self.role_mod(self, user, en, "remove")

    @app_commands.command(name="announce-showing",description="Ping people subscribed to the role for your channel.")
    async def announce_showing(self, interaction: discord.Interaction, stream_title:str, starts_in:str, schedule:str=''):
        user = interaction.user
        if str(user.id) not in self.bot.usermap:
            await interaction.response.send_message(f"You are not a theater owner! Ask Robert if you'd like to become one.", ephemeral=True)
            return
        else:
            role = discord.utils.get(self.bot.guild.roles, id = self.bot.usermap[str(user.id)])
            message = f"{role.mention} - User {user.mention} has scheduled a showing: `{stream_title}`, which starts in: `{starts_in}`.\n{self.bot.config['link_map'][str(user.id)]}"
            if schedule != '':
                schedule = schedule.replace("\\n","\n")
                message += " \nSchedule: `" + schedule + "`"
            theater_channel = discord.utils.get(self.bot.guild.channels, id=self.bot.config["announce_channels"]["theater"])
            await theater_channel.send(message)
            await interaction.response.send_message("Announcement posted!", ephemeral=True)
    
    #these are standard commands as to hide them from the / menu preventing clutter
    @commands.command(name = "add_default_react", aliases = ["adr"], hidden = True)
    async def add_default_react(self, ctx):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:
            channel = self.bot.get_channel(self.bot.config["role_channel"])
            message = await channel.fetch_message(self.bot.config["react_msgs"]["theater"])
            for emoji in self.bot.emojimap.keys():
                await message.add_reaction(emoji)
        else:
            return
    
    @commands.command(name= "remove_default_react", aliases = ["rdr"], hidden = True)
    async def remove_default_react(self, ctx):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:
            channel = self.bot.get_channel(self.bot.config["role_channel"])
            message = await channel.fetch_message(self.bot.config["react_msgs"]["theater"])
            for emoji in self.bot.emojimap.keys():
                await message.remove_reaction(emoji, self.bot.user)
        else:
            return

async def setup(bot):
    await bot.add_cog(Theaters(bot), guild = discord.Object(id = bot.guild_id))
