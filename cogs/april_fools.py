import discord
from discord.ext import commands
from discord import app_commands
import random

class Sierro(commands.Cog):
    def __init__(self, bot: commands.Bot, conn_params: dict) -> None:
        self.bot = bot
        self.health = 20000000

    @app_commands.command(name='attack', description='Help danchou attack Free-for-all-Vyrn!')
    async def attack(self, interaction: discord.Interaction) -> None:
        random.seed(401)
        success_chance = random.random()
        if success_chance >= 0.98:
            self.health = self.health - 1000000
            await interaction.response.send_message('You"ve critically attacked Free-for-all-Vyrn!!')
        elif success_chance >= 0.65:
            self.health = self.health - 250000
            await interaction.response.send_message("You've attacked Free-for-all-Vyrn!!")
        elif success_chance >= 0.40:
            self.health = self.health - 20000
            await interaction.response.send_message("You've slightly grazed Free-for-all-Vyrn!")
        else:
            await interaction.response.send_message("You missed!")
        
        if self.health < 10000000:
            await interaction.response.send_message("Free-for-all-Vyrn gestures at you menacingly")
        elif self.health < 250000:
            await interaction.response.send_message("Free-for-all-Vyrn is looking a little worse for wear...")
        elif self.health <= 0:
            await interaction.response.send_message("You've defeated Free-for-all-Vyrn!! @koipoi")
        else:
            await interaction.response.send_message("Free-for-all-Vyrn is still briming with confidence :LucioCheers:")
