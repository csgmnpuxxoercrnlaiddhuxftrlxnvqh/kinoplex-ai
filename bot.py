import sys
import discord
from discord import app_commands
import random
import json
import re


#open config
with open("config.json","r") as f:
    config = json.load(f)

token = config["token"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
client.tree = tree

admin_ids = config['admin_ids']

#specific message that contains reacts
react_msg_theater = config['react_msgs']['theater']

kinoplex_id = config['guild_id']

global kinoplex
global emojimap
global usermap

#ask responses
ask_responses = ["100%","Of course","Yes","Maybe","Impossible","No way","Don't think so","No","50/50","Robort is busy","I regret to inform you","Anon I..."]

def checked(digits):
    for idx, digit in enumerate(reversed(digits)):
     if idx + 1 >= len(digits):
        return idx + 1
     if digit != digits[::-1][idx + 1]:
        return idx + 1

def sanitize_string(string):
    global kinoplex
    #remove big  formatting
    string = re.sub('^#+','',string)
    #remove code blocks
    string = string.replace("`","")
    #remove links
    string = string.replace("https://","").replace("http://","")
    #reformat mentions
    pattern = r'<@\d+>'
    output_string = re.sub(pattern,lambda match: kinoplex.get_member(int(match.group(0).split('@')[1][:-1])).display_name,string)
    return output_string

async def role_mod(user,emoji,side):
    global emojimap
    global kinoplex
    if emoji not in emojimap: return
    role = discord.utils.get(kinoplex.roles,id=emojimap[emoji])
    if side == "add":
        print(f"User {user} reacted with {emoji}, adding role {role}")
        await user.add_roles(role)
    elif side == "remove":
        print(f"User {user} removed their {emoji} reaction, removing role {role}")
        await user.remove_roles(role)
    
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    
    global kinoplex
    global emojimap
    global usermap
    global theater_channel

    kinoplex = client.get_guild(kinoplex_id)
    print(f"Loaded server {kinoplex}")

    roles = kinoplex.roles
    emojimap = config['emoji_map']

    usermap = config['user_map']

    #react to message
    print("Reacting to role msg")
    channel = client.get_channel(config["role_channel"])
    message = await channel.fetch_message(config["react_msgs"]["theater"])
    for emoji in emojimap.keys():
        await message.add_reaction(emoji)
    
    print(f"Loading commands")
    await tree.sync(guild=kinoplex)
    print(f"Commands loaded")

    #set presence
    game = discord.Game("Kinoplex Security Cameras")
    await client.change_presence(status=discord.Status.online,activity=game)

@client.event
async def on_raw_reaction_add(payload):
    global kinoplex
    en = payload.emoji.name
    user = kinoplex.get_member(payload.user_id)
    if payload.message_id == react_msg_theater:
        if payload.user_id in admin_ids: return
        await role_mod(user,en,"add")

@client.event
async def on_raw_reaction_remove(payload):
    global kinoplex
    en = payload.emoji.name
    user = kinoplex.get_member(payload.user_id)
    if payload.message_id == react_msg_theater:
        if payload.user_id in admin_ids: return
        await role_mod(user,en,"remove")

@client.tree.command(name="announce-showing",description="Ping people subscribed to the role for your channel.",guild=discord.Object(id=kinoplex_id))
async def announce_showing(interaction: discord.Interaction, stream_title:str,starts_in:str,schedule:str=''):
    global usermap
    global kinoplex
    user = interaction.user
    if str(user.id) not in usermap:
        await interaction.response.send_message(f"You are not a theater owner! Ask Robert if you'd like to become one.",ephemeral=True)
        return
    else:
        role = discord.utils.get(kinoplex.roles,id=usermap[str(user.id)])
        message = f"{role.mention} - User {user.mention} has scheduled a showing: `{stream_title}`, which starts in: `{starts_in}`.\n{config['link_map'][str(user.id)]}"
        if schedule != '':
            message += " \nSchedule: `" + schedule + "`"
        theater_channel = discord.utils.get(kinoplex.channels,id=config["announce_channels"]["theater"])
        await theater_channel.send(message)
        await interaction.response.send_message("Announcement posted!",ephemeral=True)

@client.tree.command(name="roll",description="Roll a 4 digit number.",guild=discord.Object(id=kinoplex_id))
async def roll(interaction: discord.Interaction,message:str='🤖'):
    digits = "{:04d}".format(random.randint(0,9999))
    dubs = checked(digits)
    if message != "🤖":
        message = sanitize_string(message)[:64]
    if dubs > 1:
        msg = f"{message}: {digits[:len(digits) - dubs:]}**{digits[len(digits) - dubs::]}**"
        if dubs == 4:
            msg = "# " + msg
    else:
        msg = f"{message}: {digits}"
    await interaction.response.send_message(msg)

@client.tree.command(name="dice",description="Roll dice",guild=discord.Object(id=kinoplex_id))
async def dice(interaction: discord.Interaction,number_of_dice:int,sides:int):
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

@client.tree.command(name="callit",description="Call it.",guild=discord.Object(id=kinoplex_id))
async def callit(interaction: discord.Interaction,call:str):
    call = call.lower()
    if call not in ["heads","tails"]:
        await interaction.response.send_message("You have to call it, `heads` or `tails`, I can't do it for you.",ephemeral=True)
        return
    toss = random.randint(0,1)
    if toss == 0:
        result = "heads"
    elif toss == 1:
        result = "tails"
    
    await interaction.response.send_message(f"{interaction.user.mention} called {call}. The coin was ||`{result}`||")

@client.tree.command(name="pick",description="Pick an option from a list. Comma separated.",guild=discord.Object(id=kinoplex_id))
async def pick(interaction: discord.Interaction,comma_separated_values:str):
    csv = sanitize_string(comma_separated_values)
    vals = [x.rstrip() for x in csv[:128].split(",")]
    choice = random.choice(vals)
    msg = "Choices: " + ", ".join(vals) + f"\nPick: {choice}"
    await interaction.response.send_message(msg)

@client.tree.command(name="ask",description="Ask a question.",guild=discord.Object(id=kinoplex_id))
async def ask(interaction: discord.Interaction,question:str):
    question = sanitize_string(question)[:128]
    answer = random.choice(ask_responses)
    msg = "Question: " + question + "\nAnswer: " + answer
    await interaction.response.send_message(msg)

client.run(token)
