import discord
from discord.ext import commands
from discord import app_commands

class Sierro(commands.Cog):
    def __init__(self, bot: commands.Bot, conn_params: dict) -> None:
        self.bot = bot

    @app_commands.command(name='formula', description='Displays total rolls, total spark count, % progress to next spark')
    async def dmgFormula(self, interaction: discord.Interaction) -> None:
        pass