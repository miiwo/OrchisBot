from bs4 import BeautifulSoup
from seleniumbase import SB
import mariadb

import os
from dotenv import load_dotenv


def insert_to_skills_db(wep_name, skill_name):
    try:
        load_dotenv()
        backend_settings = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS"),
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT")),
            "database": os.getenv("DB_NAME")
        }
        connection = mariadb.connect(**backend_settings)
        dbClient = connection.cursor()

        dbClient.execute("""select id from Weapons where name = %s""", (wep_name))
        try:
            wep_id = dbClient.fetchall()[0][0]
        except:
            print('Weapon does not exist in db')
            return
        dbClient.execute("""select  id from weapon_skills where name = %s""", (skill_name))
        skill_id = dbClient.fetchall()[0][0]
        dbClient.execute("""select  count(*) from weapon_skills_relationship where wep_id = %s and wep_skill_id = %s""", (wep_id, skill_id))
        exists = dbClient.fetchall()
        if not exists:
            dbClient.execute("""insert into weapon_skills_relationship (wep_id, wep_skill_id) values (%s, %s)""", (wep_id, skill_id))
            print('Added to weapon skills relationship!')
        else:
            print('Already recorded, moving onto next...')
    except:
        print('Something happened when trying to insert into database')
    

def main():
    # Grab raw page source
    # Process it into a python object
    # Feed it into database
    wep_list = ['Bloody Scar', 'Cute Ribbon', 'Diablo Bow']
    for wep_name in wep_list:
        insert_to_skills_db(wep_name, "Dark's Might")
    # Repeat as necessary

main()