import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord.ext.commands import Greedy, Context
from discord import app_commands
from typing import Literal, Optional


class OrchisBot(commands.Bot):
    def __init__(self):
        # Intent permissions to ask for when running bot
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        super().__init__(activity=discord.Game(name='keeping DB connections open unnecessarily'), command_prefix='!', intents=intents)
        self.MY_GUILD = os.getenv('SERVER')
        self.backend_settings = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS"),
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT")),
            "database": os.getenv("DB_NAME")
        }

    async def setup_hook(self):
        print('Loading cogs...')
        await self.load_extension(f"cogs.sierro")

        print('Syncing command tree...')
        await orchis.tree.sync(guild=discord.Object(id=self.MY_GUILD))

    async def on_ready(self):
        await self.wait_until_ready()
        print('Bot online!')

    '''@commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(ctx, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None):
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()
            
            await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
            return
        
        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret+=1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")'''

load_dotenv()
orchis = OrchisBot()
orchis.run(os.getenv('TOKEN'))
