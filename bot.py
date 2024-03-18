from pathlib import Path
import json
import discord
from discord.ext import commands
import traceback


class KinoplexAI(commands.Bot):
    def __init__(self, config_file):
        self.config_file = config_file

        with open(self.config_file) as f:
            self.config = json.load(f)
        self.token = self.config["token"]
        self.guild_id = int(self.config["guild_id"])
        
        #this will be done later
        self.emojilist = self.config["emoji_map"]
        self.emojimap = []
        self.rolemap = self.config["role_map"]
        self.usermap = self.config["user_map"]
        self.react_msg_theater = self.config['react_msgs']['theater']
        
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
        for emoji in self.emojilist:
            emoji_obj = emoji
            if isinstance(emoji,int):
                emoji_obj = self.guild.get_emoji(emoji)
            self.emojimap.append(emoji_obj)

config_file = "config.json"
bot = KinoplexAI(config_file)
bot.run()
