import discord
from discord import app_commands
from discord.ext import commands
import requests


class Tmdb(commands.Cog):
    url = "https://api.themoviedb.org/3/search/"

    def __init__(self, bot):
        self.bot = bot

    def req_embed(self, type: str, params: dict):
        params["api_key"] = self.bot.config["tmdb_api_key"]

        raw_response = requests.get(f"{self.url}{type}", params = params) #would prefer to use headers here but this is smaller

        if raw_response.status_code == 200:
            #there may still be a case where status_code = 200 but there is no total_results entry
            #if it exists someone will find it sooner rather than later
            if raw_response.json()["total_results"] == 0:
                return None
            response = raw_response.json()['results'][0]
            if type == "movie":
                title = f'{response["original_title"]} ({response["release_date"].split("-")[0]})'
            if type == "tv":
                title = f'{response["original_name"]} ({response["first_air_date"].split("-")[0]})'

            embed = discord.Embed(
            title = title,
            url = f"https://www.themoviedb.org/movie/{response['id']}",
            description = response['overview'],
            color = discord.Color.dark_blue()
            )
            embed.set_thumbnail(url = f"https://image.tmdb.org/t/p/w500/{response['poster_path']}")
            embed.add_field(name = "Rating", value = f"⭐ {response['vote_average']} out of 10 over {response['vote_count']} votes")

            return embed
        else:
            print(raw_response.text)
            return discord.Embed(description = f'An API error occurred: {raw_response.status_code}')
    
    @app_commands.command(name = "movie", description = "Search TMDB for a movie")
    @app_commands.checks.cooldown(1,30)
    async def movie(self, interaction: discord.Interaction, title: str, year: str = None):
        params = {"query" : title }
        if year: params["year"] = year
        embed = self.req_embed("movie", params)

        if embed == None:
            await interaction.response.send_message("Movie not found.", ephemeral = True)
        else:
            await interaction.response.send_message(embed = embed)
    
    @app_commands.command(name = "show", description = "Search TMDB for a TV show")
    @app_commands.checks.cooldown(1,30)
    async def show(self, interaction: discord.Interaction, title: str, year: str = None):
        params = {"query" : title}
        if year: params["year"] = year
        embed = self.req_embed("tv", params)

        if embed == None:
            await interaction.response.send_message("Show not found.", ephemeral = True)
        else:
            await interaction.response.send_message(embed = embed)
    
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral = True)

async def setup(bot):
     await bot.add_cog(Tmdb(bot), guild = discord.Object(id = bot.guild_id))