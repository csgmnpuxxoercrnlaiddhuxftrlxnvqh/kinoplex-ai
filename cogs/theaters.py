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
        if emoji_id not in self.bot.mp_emoji_map: return
        role = self.bot.mp_emoji_map[emoji_id]["role"]
        if side == "add":
            print(f"User {user} reacted with {emoji_name}, adding role {role}")
            await user.add_roles(role)
        elif side == "remove":
            print(f"User {user} removed their {emoji_name} reaction, removing role {role}")
            await user.remove_roles(role)
    
    @commands.Cog.listener()  
    async def on_raw_reaction_add(self, payload):
        if(self.bot.starting): return
        en = payload.emoji.name
        eid = payload.emoji.id
        user = self.bot.guild.get_member(payload.user_id)
        if payload.message_id == self.bot.multiplexcfg["react_msg"].id:
            if payload.user_id in self.bot.owner_ids: 
                return
            await self.role_mod(self, user, en, eid, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if(self.bot.starting): return
        en = payload.emoji.name
        eid = payload.emoji.id
        user = self.bot.guild.get_member(payload.user_id)
        if payload.message_id == self.bot.multiplexcfg["react_msg"].id:
            if payload.user_id in self.bot.owner_ids: 
                return
            await self.role_mod(self, user, en, eid, "remove")

    @app_commands.command(name="announce-showing",description="Ping people subscribed to the role for your channel.")
    async def announce_showing(self, interaction: discord.Interaction, stream_title:str, starts_in:str, schedule:str='',file:discord.Attachment=None):
        user = interaction.user
        if user.id not in self.bot.mp_user_map:
            await interaction.response.send_message(f"You are not a theater owner! Ask Robert if you'd like to become one.", ephemeral=True)
            return
        else:
            role = self.bot.mp_user_map[user.id]["role"]
            message = f"{role.mention} - User {user.mention} has scheduled a showing: {stream_title}, which starts: {starts_in}.\n{self.bot.mp_user_map[user.id]['link']}"
            if schedule != '':
                schedule = schedule.replace("\\n","\n")
                message += " \nSchedule: \n" + schedule
            theater_channel = self.bot.multiplexcfg["announce_channel"]
            attachments = []
            if file:
                file_attachment = await file.to_file()
                attachments.append(file_attachment)
            await theater_channel.send(content=message,files=attachments)
            await interaction.response.send_message("Announcement posted!", ephemeral=True)
    
    @app_commands.command(name="edit-showing",description="Edit an announced showing.")
    async def edit_showing(self, interaction: discord.Interaction, message_id:str, stream_title:str, starts_in:str, schedule:str='',file:discord.Attachment=None):
        user = interaction.user
        if user.id not in self.bot.mp_user_map:
            await interaction.response.send_message(f"You are not a theater owner!", ephemeral=True)
            return
        else:
            if not message_id.isdigit():
                await interaction.response.send_message(f"Invalid message ID. Right click message and click 'Copy ID'",ephemeral=True)
            message_id = int(message_id)
            theater_channel = self.bot.multiplexcfg["announce_channel"]
            try:
                showing_message = await theater_channel.fetch_message(message_id)
            except discord.NotFound:
                await interaction.response.send_message(f"Announcement with that ID not found!",ephemeral=True)
                return
            msg_author_id = int(showing_message.content.split(" ")[3][2:-1])
            if user.id != msg_author_id:
                await interaction.response.send_message(f"You are not the author of that showing!",ephemeral=True)
                return
            role = self.bot.mp_user_map[user.id]["role"]
            message = f"{role.mention} - User {user.mention} has scheduled a showing: {stream_title}, which starts: {starts_in}.\n{self.bot.mp_user_map[user.id]['link']}"
            if schedule != '':
                schedule = schedule.replace("\\n","\n")
                message += " \nSchedule: \n" + schedule
            attachments = []
            if file:
                file_attachment = await file.to_file()
                attachments.append(file_attachment)
            await showing_message.edit(content=message,attachments=attachments)
            await interaction.response.send_message("Announcement edited!", ephemeral=True)

    #these are standard commands as to hide them from the / menu preventing clutter
    @commands.command(name = "add_default_react", aliases = ["adr"], hidden = True)
    async def add_default_react(self, ctx):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:

            message = self.bot.multiplexcfg["react_msg"]
            for emoji in self.bot.mp_emoji_map:
                await message.add_reaction(emoji["obj"])

            #for now, we just do the game reacts here too
            gmessage = self.bot.gamecfg["react_msg"]
            for emoji in self.bot.game_emoji_map:
                await gmessage.add_reaction(emoji["obj"])
        else:
            return
    
    @commands.command(name= "remove_default_react", aliases = ["rdr"], hidden = True)
    async def remove_default_react(self, ctx):
        if ctx.author.id in self.bot.owner_ids or ctx.author.id in self.bot.bot_operators:

            message = self.bot.multiplexcfg["react_msg"]
            for emoji in self.bot.mp_emoji_map:
                await message.remove_reaction(emoji["obj"], self.bot.user)
                
            gmessage = self.bot.gamecfg["react_msg"]
            for emoji in self.bot.game_emoji_map:
                await gmessage.remove_reaction(emoji["obj"], self.bot.user)
        else:
            return

async def setup(bot):
    await bot.add_cog(Theaters(bot), guild = discord.Object(id = bot.guild_id))
