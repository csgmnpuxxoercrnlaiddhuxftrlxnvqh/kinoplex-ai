import discord
from discord import app_commands
from discord.ext import commands
import time
import re

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #for now, no autoamtic role giving. just role pinging

    ping_cooldowns = {}

    #todo - figure out how to make this global so we don't have to define it everywhere
    @staticmethod
    def sanitize_string(string, guild):
        #remove big  formatting
        string = re.sub('^#+', '', string)
        #remove code blocks
        string = string.replace("`", "")
        #remove links
        string = string.replace("https://", "").replace("http://", "")
        #reformat mentions
        pattern = r'<@*\d+>'
        output_string = re.sub(pattern, lambda match: guild.get_member(int(match.group(0).split('@')[1][:-1])).display_name, string)
        return output_string

    @app_commands.command(name="game-event",description="Ping people with a specific game role.")
    async def game_event(self, interaction: discord.Interaction, game_title:str,custom_msg:str):
        user = interaction.user
        gdata = self.bot.gamedata
        if game_title not in self.bot.game_type_map:
            await interaction.response.send_message(f"To ping a game, re-send this command with one of the roles from the list-games command.",ephemeral=True)
            return
        else:
            roles = [role.id for role in user.roles]
            game_role = self.bot.game_type_map[game_title]["role"]
            if game_role.id not in roles:
                await interaction.response.send_message(f"You do not have the role for {game_title}.",ephemeral=True)
                return

        if game_title not in self.ping_cooldowns:
            self.ping_cooldowns[game_title] = 0

        timediff = time.time() - self.ping_cooldowns[game_title]

        timeout_time = 900

        if timediff < timeout_time:
            await interaction.response.send_message(f"That role is on cooldown. Try again in {round(timeout_time-timediff,2)}s",ephemeral=True)
            return
        self.ping_cooldowns[game_title] = time.time()
        sanitized_msg = self.sanitize_string(custom_msg,self.bot.guild)
        message = f"{game_role.mention} - User {user.mention} pinged for an event - {sanitized_msg}"
        await interaction.channel.send(message)
        await interaction.response.send_message("Event posted!",ephemeral=True)

    @app_commands.command(name="list-games",description="List all game roles.")
    async def list_games(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"**Game Roles:**\n\n- " + "\n- ".join(self.bot.game_type_map.keys()),ephemeral=True)
        return

    @staticmethod                                   #is this actually a static method?
    async def role_mod(self, user, emoji_name, emoji_id, side):
        if emoji_id == None:
            emoji_id = emoji_name
        if emoji_id not in self.bot.game_emoji_map: return
        role = self.bot.game_emoji_map[emoji_id]["role"]
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
        if payload.message_id == self.bot.gamecfg["react_msg"].id:
            if payload.user_id in self.bot.owner_ids: 
                return
            await self.role_mod(self, user, en, eid, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if(self.bot.starting): return
        en = payload.emoji.name
        eid = payload.emoji.id
        user = self.bot.guild.get_member(payload.user_id)
        if payload.message_id == self.bot.gamecfg["react_msg"].id:
            if payload.user_id in self.bot.owner_ids: 
                return
            await self.role_mod(self, user, en, eid, "remove")

async def setup(bot):
    await bot.add_cog(Games(bot), guild = discord.Object(id = bot.guild_id))
