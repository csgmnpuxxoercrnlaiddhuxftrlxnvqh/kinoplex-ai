import discord
from discord import app_commands
from discord.ext import commands
import random
import re

class Chat(commands.Cog):
    ask_responses = ["100%","Of course","Yes","Maybe","Impossible","No way","Don't think so","No","50/50","Robort is busy","I regret to inform you","Anon I..."]

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def checked(digits):
        for idx, digit in enumerate(reversed(digits)):
         if idx + 1 >= len(digits):
            return idx + 1
         if digit != digits[::-1][idx + 1]:
            return idx + 1
         
    @staticmethod
    def sanitize_string(string, guild):
        #remove big  formatting
        string = re.sub('^#+', '', string)
        #remove code blocks
        string = string.replace("`", "")
        #remove links
        string = string.replace("https://", "").replace("http://", "")
        #reformat mentions
        pattern = r'<@\d+>'
        output_string = re.sub(pattern, lambda match: guild.get_member(int(match.group(0).split('@')[1][:-1])).display_name, string)
        return output_string
    
    '''
    @app_commands.command(name = "say", description = "Use the Kinoplex Loudspeaker.")
    async def say(self, interaction: discord.Interaction, message:str):
        await interaction.response.send_message(self.sanitize_string(message, self.bot.guild))
    '''
        
    @app_commands.command(name = "roll",description = "Roll a 4 digit number.")
    @app_commands.checks.cooldown(1,30)
    async def roll(self, interaction: discord.Interaction, message: str ='🤖'):
        digits = "{:04d}".format(random.randint(0,9999))
        dubs = self.checked(digits)
        if message != "🤖":
            message = self.sanitize_string(message, self.bot.guild)[:128]
        if dubs > 1:
            msg = f"{message}: {digits[:len(digits) - dubs:]}**{digits[len(digits) - dubs::]}**"
            if dubs == 4:
                msg = "# " + msg
        else:
            msg = f"{message}: {digits}"
        await interaction.response.send_message(msg)

    @app_commands.command(name = "dice",description = "Roll dice")
    @app_commands.checks.cooldown(1,30)
    async def dice(self, interaction: discord.Interaction, number_of_dice: int, sides:int):
        total = 0
        if sides < 1:
            sides = 1
        if sides > 100:
            sides = 100
        if number_of_dice > 1000:
            number_of_dice = 1000
        if number_of_dice < 1:
            number_of_dice = 1
        for _ in range(number_of_dice):
            total += random.randint(1,sides)
        await interaction.response.send_message(f"Rolling {number_of_dice}d{sides}: {total}")

    @app_commands.command(name = "callit",description = "Call it.")
    @app_commands.checks.cooldown(1,30)
    async def callit(self, interaction: discord.Interaction, call: str):
        call = call.lower()
        if call not in ["heads", "tails"]:
            await interaction.response.send_message("You have to call it, `heads` or `tails`, I can't do it for you.", ephemeral = True)
            return
        toss = random.randint(0,1)
        if toss == 0:
            result = "heads"
        elif toss == 1:
            result = "tails"
        await interaction.response.send_message(f"{interaction.user.mention} called {call}. The coin was ||`{result}`||")

    @app_commands.command(name= "pick", description= "Pick an option from a list. Comma separated.")
    @app_commands.checks.cooldown(1,30)
    async def pick(self, interaction: discord.Interaction, comma_separated_values: str):
        csv = self.sanitize_string(comma_separated_values, self.bot.guild)
        vals = [x.rstrip() for x in csv[:256].split(",")]
        choice = random.choice(vals)
        msg = "Choices: " + ", ".join(vals) + f"\nPick: {choice}"
        await interaction.response.send_message(msg)
    
    @app_commands.command(name= "ask",description= "Ask a question.")
    @app_commands.checks.cooldown(1,30)
    async def ask(self, interaction: discord.Interaction, question: str):
        question = self.sanitize_string(question, self.bot.guild)[:128]
        answer = random.choice(self.ask_responses)
        msg = "Question: " + question + "\nAnswer: " + answer
        await interaction.response.send_message(msg)

    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral = True)

async def setup(bot):
    await bot.add_cog(Chat(bot), guild = discord.Object(id = bot.guild_id)) #figure out how to reference the guild without the id