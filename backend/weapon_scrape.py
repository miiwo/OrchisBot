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
            "database": os.getenv("WEP_DB_NAME")
        }
        connection = mariadb.connect(**backend_settings)
        dbClient = connection.cursor()

        dbClient.execute("SELECT id FROM Weapons WHERE name = ?", (wep_name,))
        try:
            wep_id = dbClient.fetchall()[0][0]
        except:
            print('Weapon does not exist in db: ' + wep_name)
            return
        dbClient.execute("SELECT id FROM weapon_skills WHERE name = ?", (skill_name,))
        try:
            skill_id = dbClient.fetchall()[0][0]
        except:
            print('Skill name does not exist in db: ' + skill_name)
            return
        dbClient.execute("SELECT count(*) FROM weapon_skills_relationship WHERE wep_id = ? AND wep_skill_id = ?", (wep_id, skill_id))
        exists = dbClient.fetchall()[0][0]
        if not exists:
            dbClient.execute("INSERT INTO weapon_skills_relationship (wep_id, wep_skill_id) VALUES (?, ?)", (wep_id, skill_id))
            connection.commit()
            connection.close()
            print('Added to weapon skills relationship!')
        else:
            print('Already recorded, moving onto next...')
    except Exception as e:
        print('Something happened when trying to insert into database')
        raise e
    

def main():
    # Grab raw page source
    # Process it into a python object
    # Feed it into database
    wep_list = ['Distant Requiem', "Miming's Baselard", 'Shadow Viperlance', 'Unparalleled Chopsticks']
    for wep_name in wep_list:
        insert_to_skills_db(wep_name, "Hatred's Celere")
    # Repeat as necessary

main()
