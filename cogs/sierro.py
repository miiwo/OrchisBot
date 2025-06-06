import discord
from discord.ext import commands
from discord import app_commands
import math
import mariadb
import sys

class Sierro(commands.Cog):
    def __init__(self, bot: commands.Bot, conn_params: dict) -> None:
        self.bot = bot
        self.db_params = conn_params

    @app_commands.command(name='show', description='Displays total rolls, total spark count, % progress to next spark')
    async def displayTotal(self, interaction: discord.Interaction) -> None:
        try:
            data = await self.fetchFromBackend(interaction.user.id)

            if data is None:
                await interaction.response.send_message("You haven't set your spark count yet. Do so with the `/qs` command!")
                return

            data['name'] = interaction.user.display_name
            data['profile_pic'] = interaction.user.display_avatar

            spark_embed = await self.createSparkEmbed(data)

            await interaction.response.send_message(embed=spark_embed)
        except IOError as ioe:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            print(f"ORCHIS BOT ERROR ({exception_type}) {ioe}. Line traceback: {exception_traceback.tb_lineno}")
            await interaction.response.send_message('Could not connect to the backend for some reason... Please try again shortly or contact @koipoi')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            print(f"ORCHIS BOT ERROR ({exception_type}) {e}. Line traceback: {exception_traceback.tb_lineno}")
            await interaction.response.send_message('Could not display total sparks for some reason... Please try again shortly or contact @koipoi')


    @app_commands.command(name='qs', description='Sets the users crystals, 10-pull tickets, and singles to the number provided')
    @app_commands.describe(crystal='How many crystals do you have?', ten_pull_tix='How many ten-pull tickets do you have?', single_pull_tix='How many single pull tickets do you have?')
    async def quicksave(self, interaction: discord.Interaction, crystal: int, ten_pull_tix: int, single_pull_tix: int) -> None:
        insert_successful = await self.insertToBackend(interaction.user.id, crystal, ten_pull_tix, single_pull_tix)

        if insert_successful:
            data = await self.fetchFromBackend(interaction.user.id)

            data['name'] = interaction.user.display_name
            data['profile_pic'] = interaction.user.display_avatar

            spark_embed = await self.createSparkEmbed(data)

            await interaction.response.send_message(content=f'Your sparks have been saved into the bot {f"Embed cannot be displayed at this time however :(" if spark_embed is None else ""}', embed=spark_embed)
        else:
            await interaction.response.send_message('Your sparks did not save properly into the bot, please try again shortly or contact @koipoi')

    @app_commands.command(name='setsparktarget', description='Type the name of the character(s) or weapon(s) you want to spark')
    @app_commands.describe(target='Your character/weapon target')
    async def sparkTarget(self, interaction: discord.Interaction, target: str) -> None:
        set_spark_success = await self.insertTargetToBackend(interaction.user.id, target)

        if set_spark_success:
            await interaction.response.send_message(f'Your spark target has been set to: `{target}`!')
        else:
            await interaction.response.send_message('Something went wrong with setting your spark target :( Please message koipoi to notify them of the issue')


    async def createSparkEmbed(self, data):
        try:
            embed = discord.Embed(
                title=data['name'],
                color=0x336EFF
            )

            embed.set_thumbnail(url=data['profile_pic'])

            embed.add_field(name='Crystals', value=data['crystals'], inline=True)
            embed.add_field(name='Tickets', value=data['single_tix'], inline=True)
            embed.add_field(name='10-Part Tickets', value=data['tenpull_tix'], inline=True)

            draws = math.floor(data['crystals'] / 300) + data['tenpull_tix'] * 10 + data['single_tix']
            sparks = math.floor(draws / 300)
            percent_to_next_spark = math.floor(draws%300/3)

            embed.add_field(name='Progress', value=f'`Spark #{sparks + 1} [{self.createProgressBar(draws)}] {percent_to_next_spark}%`', inline=False)
            if sparks > 0:
                embed.add_field(name='Sparks', value=sparks, inline=True)

            embed.add_field(name='Draws', value=draws, inline=True)

            if data['target'] != "NULL":
                embed.add_field(name='Spark Target', value=data['target'], inline=False)
            else:
                embed.add_field(name='Spark Target', value='No spark target set.', inline=False)

        except Exception as e:
            print(f"ORCHIS BOT ERROR in createSparkEmbed function. {e}")
            embed = None

        return embed

    def createProgressBar(self, draws):
        if draws%300 == 0:
            return " "*16

        ticks = math.floor(15 / (100/(draws%300/3)))
        return "="*ticks + ">" + " "*(15 - ticks)

    '''
    Function that will fetch data from a backend.
    It will return a dictionary if there is data to be fetched. If there is none, it will return None.
    If there are errors regarding DB operations / connection, this function will raise an error.
    '''
    async def fetchFromBackend(self, key : str) -> dict:
        result = None

        try:
            db_connection = mariadb.connect(**self.db_params)
            db_connection.auto_reconnect = True
            db_client = db_connection.cursor()

            db_client.execute("SELECT crystals,tenpull,onepull,spark_target FROM sparks where id=?", (key,))
            data = db_client.fetchone()

            if data is not None:
                result = { "crystals": data[0], "tenpull_tix": data[1], "single_tix": data[2], "target": data[3]}

        except mariadb.Error as e:
            print(f"OrchisBot Error: {e}")
            raise e
        else:
            db_connection.close()

        return result

    '''
    Function that will insert the spark data into a backend.
    It will return a boolean with True indicating successful insertion, and False indicating unsuccessful insertion.
    This function will not raise an error if there are DB issues, and will simply send back to caller a unsuccessful insertion.
    '''
    async def insertToBackend(self, id, crystal: int, tenpull: int, singlepull: int) -> bool:
        try:
            db_connection = mariadb.connect(**self.db_params)
            db_connection.auto_reconnect = True
            db_client = db_connection.cursor()

            data = await self.fetchFromBackend(id)

            if data is None:
                db_client.execute("INSERT INTO sparks (id, crystals, tenpull, onepull) VALUES (?,?,?,?)", (id, crystal, tenpull, singlepull))
            else:
                db_client.execute("UPDATE sparks set crystals=?, tenpull=?, onepull=? where id=?", (crystal, tenpull, singlepull, id))

            db_connection.commit()

        except Exception as e:
            print(f"OrchisBot Error: Inserting into backend. {e}")
            return False
        else:
            db_connection.close()

        return True

    async def insertTargetToBackend(self, id, target: str) -> bool:
        try:
            db_connection = mariadb.connect(**self.db_params)
            db_connection.auto_reconnect = True
            db_client = db_connection.cursor()

            data = await self.fetchFromBackend(id)

            if data is None:
                db_client.execute("INSERT INTO sparks (id, crystals, tenpull, onepull, spark_target) VALUES (?,0,0,0,?)", (id, target))
            else:
                db_client.execute("UPDATE sparks set spark_target=? where id=?", (target, id))

            db_connection.commit()
        except Exception as e:
            print(f"OrchisBot Error: Inserting spark target into backend. {e}")
            return False
        else:
            db_connection.close()

        return True

async def setup(bot: commands.Bot):
    print("setting up sierro cog...")
    await bot.add_cog(Sierro(bot, bot.backend_settings), guilds=[discord.Object(id=bot.MY_GUILD)])
