# Orchis Bot

## How to run
Setup the backend DB. This bot uses an SQL backend at the moment, and it can be setup by running the `setup.sql` script in the `backend` folder. 
Please replace values surrounded by <> with your own values in the setup script.

Setup the `.env` file with the following values:
- DB, DB User, DB Pass, DB Host
- Discord Token
- Discord Server ID

On the command line, run this first:
`$ pip install -r requirements.txt`
Wait for it to finish downloading all of the necessary packages.

Then run this for the bot to go online.
`$ python bot.py`