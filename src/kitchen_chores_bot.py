# =================================
# Imports
# =================================
import asyncio
import discord
from discord.ext.commands import Bot
from discord.flags import Intents

import datetime
import logging
import os
import sys

import util


# =================================
# Logging setup
# =================================
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
  '[%(levelname)s] {%(funcName)s | %(filename)s} %(asctime)s:  %(message)s')

file_handler = logging.FileHandler(
  filename=util.get_logs_folder() / 'kitchen-chores-bot-{}.log'.format(
    datetime.datetime.now()),
  encoding='utf-8', mode='w')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARNING)
logger.addHandler(console_handler)


# =================================
# Bot parameters
# =================================
COMMAND_PREFIX = '!'
_START_OF_TIME = datetime.datetime(2020, 4, 20, 0, 0, 0, 0)


# =================================
# Algorithm DS & bot initialization
# =================================
_guild = None
_role = None
_users = []

intents = discord.Intents.default()
intents.members = True
bot = Bot(COMMAND_PREFIX, intents=intents)


# =================================
# Bot Commands
# =================================
@bot.event
async def on_ready():
  global _guild
  global _role
  global _users

  _guild = next(filter(lambda g: g.id == int(os.getenv('GUILD')), bot.guilds))
  _role = next(filter(lambda r: r.id == int(os.getenv('ROLE')), _guild.roles))
  bot_role = next(filter(lambda r: r.name == 'bot', _guild.roles))

  _users = []
  for member in _guild.members:
    if _role in member.roles and bot_role not in member.roles:
      _users.append(member)

  server_str = """

        ██████╗██████╗███╗   ███╗██████╗███╗   ████████╗              
        ██╔═══████╔══██████╗ ██████╔═══██████╗  ████╔══██╗             
        ██║   ████████╔██╔████╔████║   ████╔██╗ ████║  ██║             
        ██║   ████╔══████║╚██╔╝████║   ████║╚██╗████║  ██║             
        ╚██████╔██║  ████║ ╚═╝ ██╚██████╔██║ ╚██████████╔╝             
        ╚═════╝╚═╝  ╚═╚═╝     ╚═╝╚═════╝╚═╝  ╚═══╚═════╝              
                                                                      
████████╗  ██╗██████╗██████╗███████╗        ███╗   ███╗██████╗██████╗ 
██╔════██║  ████╔═══████╔══████╔════╝        ████╗ ██████╔════╝██╔══██╗
██║    █████████║   ████████╔█████╗          ██╔████╔████║  █████████╔╝
██║    ██╔══████║   ████╔══████╔══╝          ██║╚██╔╝████║   ████╔══██╗
╚████████║  ██╚██████╔██║  █████████╗        ██║ ╚═╝ ██╚██████╔██║  ██║
╚═════╚═╝  ╚═╝╚═════╝╚═╝  ╚═╚══════╝        ╚═╝     ╚═╝╚═════╝╚═╝  ╚═╝

Registered Users:
{}

Now Serving.\n""".format('\n'.join(u.nick or u.name for u in _users))

  logger.info(server_str)
  print(server_str)


@bot.command(name='today', help='Return the person who is on-call today')
async def on_call_today(ctx):
  return await ctx.message.channel.send(
    '<@{}> is responsible for the kitchen tonight!'.format(_users[0].id))

  
@bot.command(name='schedule', help='List the schedule for the seven days',
             pass_context=True)
async def schedule(ctx):
  pass

  
if __name__ == '__main__':
  util.load_env()
  bot.run(os.getenv('TOKEN'))