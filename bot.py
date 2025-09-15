from pathlib import Path
import json
import discord
from discord.ext import commands
import traceback
import threading
import asyncio

def input_loop(bot):
    while True:
        try:
            msg = input("Message to send: ")
            if msg:
                coro = bot.mainchannel.send(content=msg)
                asyncio.run_coroutine_threadsafe(coro, bot.loop)
        except KeyboardInterrupt:
            print("Interrupted.")
            asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)
            break

class KinoplexAI(commands.Bot):
    def __init__(self, config_file):
        self.config_file = config_file
        self.starting = True
        with open(self.config_file) as f:
            self.config = json.load(f)

        self.token = self.config["token"]
        self.guild_id = self.config["guild_id"]
        
        self.multiplexcfg = self.config["multiplex_config"]
        self.gamecfg = self.config["game_config"]
        self.main_channel = self.config["main_channel"]
        
        self.start_extensions = [x.stem for x in Path("cogs").glob("*.py")]

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents = intents, command_prefix= ".")    

        self.owner_ids = self.config["admin_ids"]                   
        self.bot_operators = self.config["bot_operators"]
        self.activity = discord.Activity(type = discord.ActivityType.watching, name = self.config["presence"])

    def run(self):
        super().run(self.token)
    
    async def setup_hook(self):

        for extension in self.start_extensions:
            try:
                await self.load_extension(f"cogs.{extension}")
            except Exception:
                print(f"{extension} extension failed to load")
                traceback.print_exc()
            else:
                print(f"Loaded extention {extension}") 

    async def on_ready(self):            
        self.guild = self.get_guild(self.guild_id)          #required AFTER connecting
        print(f"Connected to {self.guild} as {self.user.display_name}")

        #multiplex handling
        self.mp_emoji_map = {}
        self.mp_user_map = {}
        for cfg in self.multiplexcfg["multiplexes"]:
            emoji_obj = cfg["emote"]
            if isinstance(cfg["emote"],int):
                emoji_obj = self.guild.get_emoji(cfg["emote"])

            role = discord.utils.get(self.guild.roles, id=cfg["role"])

            self.mp_emoji_map[cfg["emote"]] = {"role":role,"obj":emoji_obj,"role_id":cfg["role"]}

            self.mp_user_map[cfg["user_id"]] = {"role":role,"link":cfg["channel_link"],"role_id":cfg["role"]}

        self.multiplexcfg["emote_role_channel"] = self.get_channel(self.multiplexcfg["role_channel"])
        self.multiplexcfg["announcement_channel"] = self.get_channel(self.multiplexcfg["announce_channel"])
        self.multiplexcfg["react_message"] = await self.multiplexcfg["emote_role_channel"].fetch_message(self.multiplexcfg["react_msg"])

        #game handling
        self.game_emoji_map = {}
        self.game_type_map = {}
        for cfg in self.gamecfg["games"]:
            emoji_obj = cfg["emote"]
            if isinstance(cfg["emote"],int):
                emoji_obj = self.guild.get_emoji(cfg["emote"])

            role = discord.utils.get(self.guild.roles, id=cfg["role"])

            self.game_emoji_map[cfg["emote"]] = {"role":role,"obj":emoji_obj,"role_id":cfg["role"]}
            self.game_type_map[cfg["type"]] = {"role":role,"role_id":cfg["role"]}

        self.gamecfg["emote_role_channel"] = self.get_channel(self.gamecfg["role_channel"])
        self.gamecfg["react_message"] = await self.gamecfg["emote_role_channel"].fetch_message(self.gamecfg["react_msg"])
        self.mainchannel = self.get_channel(self.main_channel)

        print(f"Successfully loaded configs")
        self.starting = False

        threading.Thread(target=input_loop, args=(self,), daemon=True).start()

config_file = "config.json"
bot = KinoplexAI(config_file)
bot.run()
