import discord
from discord import app_commands
from discord.ext import commands

class Theaters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod                                   #is this actually a static method?
    async def role_mod(self, user, emoji_name, emoji_id, side):
        if emoji_id == None:
            emoji_id = emoji_name
        if emoji_id not in self.bot.emojilist: return
        role = discord.utils.get(self.bot.guild.roles, id=self.bot.rolemap[self.bot.emojilist.index(emoji_id)])
        if side == "add":
            print(f"User {user} reacted with {emoji_name}, adding role {role}")
            await user.add_roles(role)
        elif side == "remove":
            print(f"User {user} removed their {emoji_name} reaction, removing role {role}")
            await user.remove_roles(role)
    
    @commands.Cog.listener()  
    async def on_raw_reaction_add(self, payload):
        en = payload.emoji.name
        eid = payload.emoji.id
        user = self.bot.guild.get_member(payload.user_id)
        if payload.message_id == self.bot.react_msg_theater:
            if payload.user_id in self.bot.owner_ids: 
                return
            await self.role_mod(self, user, en, eid, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        en = payload.emoji.name
        eid = payload.emoji.id
        user = self.bot.guild.get_member(payload.user_id)
        if payload.message_id == self.bot.react_msg_theater:
            if payload.user_id in self.bot.owner_ids: 
                return
            await self.role_mod(self, user, en, eid, "remove")

    @app_commands.command(name="announce-showing",description="Ping people subscribed to the role for your channel.")
    async def announce_showing(self, interaction: discord.Interaction, stream_title:str, starts_in:str, schedule:str=''):
        user = interaction.user
        if str(user.id) not in self.bot.usermap:
            await interaction.response.send_message(f"You are not a theater owner! Ask Robert if you'd like to become one.", ephemeral=True)
            return
        else:
            index = self.bot.usermap.index((str(user.id)))
            role = discord.utils.get(self.bot.guild.roles, id = self.bot.rolemap[index])
            message = f"{role.mention} - User {user.mention} has scheduled a showing: {stream_title}, which starts: {starts_in}.\n{self.bot.config['link_map'][index]}"
            if schedule != '':
                schedule = schedule.replace("\\n","\n")
                message += " \nSchedule: \n" + schedule
            theater_channel = discord.utils.get(self.bot.guild.channels, id=self.bot.config["announce_channels"]["theater"])
            await theater_channel.send(message)
            await interaction.response.send_message("Announcement posted!", ephemeral=True)
    
    @app_commands.command(name="edit-showing",description="Edit an announced showing.")
    async def edit_showing(self, interaction: discord.Interaction, message_id:str, stream_title:str, starts_in:str, schedule:str=''):
        user = interaction.user
        if str(user.id) not in self.bot.usermap:
            await interaction.response.send_message(f"You are not a theater owner!", ephemeral=True)
            return
        else:
            if not message_id.isdigit():
                await interaction.response.send_message(f"Invalid message ID. Right click message and click 'Copy ID'",ephemeral=True)
            message_id = int(message_id)
            theater_channel = discord.utils.get(self.bot.guild.channels, id=self.bot.config["announce_channels"]["theater"])
            try:
                showing_message = await theater_channel.fetch_message(message_id)
            except discord.NotFound:
                await interaction.response.send_message(f"Announcement with that ID not found!",ephemeral=True)
                return
            msg_author_id = int(showing_message.content.split(" ")[3][2:-1])
            if user.id != msg_author_id:
                await interaction.response.send_message(f"You are not the author of that showing!",ephemeral=True)
                return
            index = self.bot.usermap.index((str(user.id)))
            role = discord.utils.get(self.bot.guild.roles, id = self.bot.rolemap[index])
            message = f"{role.mention} - User {user.mention} has scheduled a showing: {stream_title}, which starts: {starts_in}.\n{self.bot.config['link_map'][index]}"
            if schedule != '':
                schedule = schedule.replace("\\n","\n")
                message += " \nSchedule: \n" + schedule
            await showing_message.edit(content=message)
            await interaction.response.send_message("Announcement edited!", ephemeral=True)

    #these are standard commands as to hide them from the / menu preventing clutter
    @commands.command(name = "add_default_react", aliases = ["adr"], hidden = True)
    async def add_default_react(self, ctx):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:
            channel = self.bot.get_channel(self.bot.config["role_channel"])
            message = await channel.fetch_message(self.bot.config["react_msgs"]["theater"])
            for emoji in self.bot.emojimap:
                await message.add_reaction(emoji)
            #for now, we just do the game reacts here too
            gmessage = await channel.fetch_message(self.bot.gamedata["react_msg"])
            for emoji in self.bot.gameemojimap:
                await gmessage.add_reaction(emoji)
        else:
            return
    
    @commands.command(name= "remove_default_react", aliases = ["rdr"], hidden = True)
    async def remove_default_react(self, ctx):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:
            channel = self.bot.get_channel(self.bot.config["role_channel"])
            message = await channel.fetch_message(self.bot.config["react_msgs"]["theater"])
            for emoji in self.bot.emojimap:
                await message.remove_reaction(emoji, self.bot.user)
            gmessage = await channel.fetch_message(self.bot.gamedata["react_msg"])
            for emoji in self.bot.gameemojimap:
                await gmessage.remove_reaction(emoji, self.bot.user)
        else:
            return

async def setup(bot):
    await bot.add_cog(Theaters(bot), guild = discord.Object(id = bot.guild_id))
