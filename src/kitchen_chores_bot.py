import datetime
import os
from discord import guild

from discord.flags import Intents
import util

import discord
from discord.ext.commands import Bot


COMMAND_PREFIX = '!'
_guild = None
_role = None
_users = []


intents = discord.Intents.default()
intents.members = True
bot = Bot(COMMAND_PREFIX, intents=intents)


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

  print("""
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
    """)
  print('Registered Users:')
  for u in _users:
    print(u.nick)

  print('Now serving')


@bot.command(name='init', help='Reinitialize the bot. Refreshes all data',
             pass_context=True)
async def initialize(ctx):
  role = discord.utils.get(ctx.message.server.roles, id=os.getenv('ROLE'))

  
if __name__ == '__main__':
  util.load_env()
  bot.run(os.getenv('TOKEN'))