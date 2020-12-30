# =================================
# Imports
# =================================
import asyncio
import discord
from discord.ext import commands
from discord.ext import tasks
from discord.flags import Intents

import calendar
import datetime
import logging
import os
import pytablewriter
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
RESET_TIME = datetime.time(4, 20, 0, 0)
NOTIFICATION_FREQUENCY = {'minutes': 30.0}


# =================================
# Algorithm DS & bot initialization
# =================================
_guild = None
_role = None
_users = []
_signed_off = False

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(COMMAND_PREFIX, intents=intents)


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

Configured to notify every {} {}.

Now Serving.\n""".format('\n'.join(u.nick or u.name for u in _users),
                         list(NOTIFICATION_FREQUENCY.keys())[0],
                         list(NOTIFICATION_FREQUENCY.items())[0])

  logger.info(server_str)
  print(server_str)


@bot.command(name='today', help='Return the person who is on-call today')
async def on_call_today(ctx):
  await ctx.message.channel.send(
    '<@{}> is responsible for the kitchen tonight!'.format(_users[0].id))

  
@bot.command(name='schedule', help='List the schedule for the seven days')
async def schedule(ctx):
  await ctx.message.channel.send('```{}```'.format(generate_schedule()))


@bot.command(name='swap', help='Swap on call position with chosen person')
async def swap(ctx, member: discord.Member):
  author_id = _users.index(ctx.message.author)
  swapee_id = _users.index(member)

  _users[swapee_id] = _users[author_id]
  _users[author_id] = member
  
  await ctx.message.channel.send('Users have been switched! The new schedule '
                                 'should be as follows:')
  await ctx.message.channel.send('```{}```'.format(generate_schedule()))

  
@bot.command(name='signoff', help='Sign off the specified member for today')
async def signoff(ctx, member: discord.Member):
  if member != _users[0]:
    return await ctx.message.channel.send(
      'The only person who can be signed off is the one actively on duty. '
      'Currently, that is {}.'.format(_users[0].nick or _users[0].name))

  _users.append(_users.pop(0))
  _signed_off = True
  
  return await ctx.message.channel.send(
    '<@{}> has been signed off for tonight!'.format(member.nick or member.name))

  
def generate_schedule() -> str:
  """Generate a markdown table of the next 7 days' schedule."""
  dow = datetime.datetime.today().weekday()
  
  if not _signed_off:
    days = ['{} (today)'.format(calendar.day_abbr[dow])]
  else:
    days = ['{} (tmrw)'.format(calendar.day_abbr[dow + 1])]
  people = [_users[0].nick or _users[0].name]

  for i in range(1, 7):
    if not _signed_off:
      day_name = calendar.day_abbr[(dow + i) % 7]
    else:
      day_name = calendar.day_abbr[(dow + i + 1) % 7]
    days.append(day_name)

    user = _users[i % len(_users)]
    people.append(user.nick or user.name)

  writer = pytablewriter.MarkdownTableWriter(
    headers=days, value_matrix=[people])

  return writer.dumps()

  
if __name__ == '__main__':
  util.load_env()
  bot.run(os.getenv('TOKEN'))