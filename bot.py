# -*- encoding: utf-8 -*-
from __future__ import annotations
import disnake
from disnake.ext import commands
from data.settings import *
from logging import *

def main():
    # define logging
    basicConfig(
        handlers=(
            FileHandler(LOGGING_PATH),
            StreamHandler()
        ), 
        format='[%(asctime)s | %(levelname)s]: %(message)s', 
        datefmt='%m.%d.%Y %H:%M:%S',
        level=INFO
    )
    # define bot vars
    bot = commands.InteractionBot()
    bot.status = disnake.Streaming('Testing')
    bot.load_extensions(EXTENSIONS_PATH)
    info('Extensions loaded!')
    # define events
    @bot.event
    async def on_ready():
        info('Bot started!') # show info
    # run bot
    bot.run(open(TOKEN_PATH, 'r').read())

if __name__ == '__main__':
    main()