import discord
from discord.ext import commands
from discord import app_commands
import mariadb
import sys

class WeaponsAndCharas(commands.Cog):
    def __init__(self, bot: commands.Bot, conn_params: dict) -> None:
        self.bot = bot

        try:
            self.db_connection = mariadb.connect(**conn_params)
            self.db_client=self.db_connection.cursor()
        except mariadb.Error as e:
            print(f"Something went wrong with connecting to the DB. Error: {e}")
            raise(e)

    @app_commands.command(name='wep_info', description='Get the info for a weapon you search for via name')
    @app_commands.describe(wep_name='Name of weapon to get info for')
    async def displayWepInfo(self, interaction: discord.Interaction, wep_name: str) -> None:
        try:
            data = await self.fetchWeaponFromBackend(wep_name)
            if data is None:
                await interaction.response.send_message(f'You searched for: {wep_name}. There was no data in the database for that wep name.')
                return
            
            weapon_pic = discord.File(data['pic'], filename="gbf_image.jpg") if data['pic'] is not None else None
            wepEmbed = await self.createWeaponEmbed(data, weapon_pic, "gbf_image.jpg")

            if weapon_pic is not None:
                await interaction.response.send_message(file=weapon_pic, embed=wepEmbed)
            else:
                await interaction.response.send_message(embed=wepEmbed)

        except IOError as ioe:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            print(f"ERROR ({exception_type}) {ioe}. Line traceback: {exception_traceback.tb_lineno}")

            await interaction.response.send_message('Could not connect to the backend for some reason. Please try again shortly or contact the dev koipoi')

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            print(f"ERROR ({exception_type}) {e}. Line traceback: {exception_traceback.tb_lineno}")

            await interaction.response.send_message('There was an error with trying to get the weapon. Please try again shortly or contact the dev koipoi')

    async def createWeaponEmbed(self, data, file_pic: discord.File, filename: str):
        embed = discord.Embed(
                    title=data['name'],
                    color=0x336EFF,
                    description=data['ca_desc']
        )

        if file_pic is not None:
            embed.set_image(url=f'attachment://{filename}')

        embed.add_field(name='Element', value=data['element'].title(), inline=True)
        embed.add_field(name='Weapon Type', value=data['weapon_type'].title(), inline=True)
        if data['wep_series'] is not None:
            embed.add_field(name='Series', value=data['wep_series'].title(), inline=True)


        for idx, wep_skill in enumerate(data["wep_skills"]):
            embed.add_field(name=f'Weapon Skill {idx+1}', value=f'*{wep_skill[0]}*\n{wep_skill[2]} | {wep_skill[3]}%\n{wep_skill[1]}', inline=False)


        return embed
        
    async def fetchWeaponFromBackend(self, name: str) -> dict:
        try:
            # Look in alias table
            self.db_client.execute("SELECT id from WepNameAlias where name like ?", (name,))
            alias_id = self.db_client.fetchone()

            if alias_id is None:
                self.db_client.execute("SELECT name, element, wep_type, picture_small, id, ca_desc, lvl_twohundred_atk, lvl_onefifty_atk, lvl_hundred_atk FROM Weapons WHERE name like ?", (name,))
            else:
                self.db_client.execute("SELECT name, element, wep_type, picture_small, id, ca_desc, lvl_twohundred_atk, lvl_onefifty_atk, lvl_hundred_atk FROM Weapons WHERE id = ?", (alias_id[0],))
            
            wep_data = self.db_client.fetchone()
            if wep_data is None:
                return None
            
            if wep_data[6] is None:
                if wep_data[7] is None:
                    self.db_client.execute("SELECT name, description, boost_type, skill_perc_lvl_ten FROM weapon_skills WHERE id in (SELECT weapon_skill_id FROM weapon_skills_relationship WHERE weapon_id = ?)", (wep_data[4],))
                else:
                    self.db_client.execute("SELECT name, description, boost_type, skill_perc_lvl_fifteen FROM weapon_skills WHERE id in (SELECT weapon_skill_id FROM weapon_skills_relationship WHERE weapon_id = ?)", (wep_data[4],))

            else:
                self.db_client.execute("SELECT name, description, boost_type, skill_perc_lvl_twenty FROM weapon_skills WHERE id in (SELECT weapon_skill_id FROM weapon_skills_relationship WHERE weapon_id = ?)", (wep_data[4],))
            skill_data = self.db_client.fetchall()

            wep_series = None
            for series_name in ['epic', 'vyrmament', 'olden primal', 'ultima', 'cosmos', 'vintage', 'superlative', 'illustrious', 'sephira', 'seraphic', 'bahamut', 'primal', 'magna', 'grand', 'regalia', 'rose', 'relic', 'ccw', 'rusted', 'rotb', 'revenant', 'replica', 'xeno', 'hollowsky', 'dark opus', 'astral', 'draconic', 'ennead', '6D', 'nwf', 'militis', 'malice', 'menace', 'pg', 'revans', 'world']:
                try:
                    self.db_client.execute(f"SELECT id from {series_name} where id = ?", (wep_data[4],))
                    temp_wep_series = self.db_client.fetchone()
                    if temp_wep_series is not None:
                        wep_series = series_name
                        break
                except Exception as e:
                    pass

            return {"name": wep_data[0], "element": wep_data[1], "weapon_type": wep_data[2], "pic": wep_data[3], "wep_skills": skill_data, "wep_series": wep_series, "ca_desc": wep_data[5]} if wep_data is not None else None

        except mariadb.Error as e:
            print(f"Error: {e}")
            raise e


async def setup(bot: commands.Bot):
    print('setting up weapons and chara cog...')
    await bot.add_cog(WeaponsAndCharas(bot, bot.wep_backend_settings), guilds=[discord.Object(id=bot.MY_GUILD)])
