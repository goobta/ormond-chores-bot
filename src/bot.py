# =================================
# Imports
# =================================
from discord.ext import commands
from discord.ext import tasks
from discord.flags import Intents

import asyncio
import discord
import calendar
import datetime
import logging
import os
import pytablewriter
import sys

import scheduler
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

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(COMMAND_PREFIX, intents=intents)

sch: scheduler.Scheduler = None
NOTIFICATION_FREQUENCY = {'minutes': 30.0}


# =================================
# Bot Commands
# =================================
@bot.event
async def on_ready():
  guild = next(filter(lambda g: g.id == int(os.getenv('GUILD')), bot.guilds))
  channel = next(filter(lambda c: c.id == int(os.getenv('CHANNEL')), 
                      guild.channels))
  role = next(filter(lambda r: r.id == int(os.getenv('ROLE')), guild.roles))
  bot_role = next(filter(lambda r: r.name == 'bot', guild.roles))

  users = []
  for member in guild.members:
    if role in member.roles and bot_role not in member.roles:
      users.append(member)

  global sch
  sch = scheduler.Scheduler(guild, channel, users)

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

Now Serving.\n""".format('\n'.join(u.nick or u.name for u in users),
                         list(NOTIFICATION_FREQUENCY.values())[0],
                         list(NOTIFICATION_FREQUENCY.keys())[0])

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


@tasks.loop(**NOTIFICATION_FREQUENCY)
async def notify():
  global _signed_off
  curr_time = datetime.datetime.now().time()

  if not _signed_off and (curr_time >= NOTIFICATION_START or \
     (curr_time <= RESET_TIME)):
    await _channel.send('Chore whore reminder: <@{}> is responsible for '
                        'the kitchen tonight!'.format(_users[0]))
  elif _signed_off and curr_time >= RESET_TIME:
    _signed_off = False


@notify.before_loop
async def notifications_init():
  """Sleep so that the notifications start on the hour."""
  next_hour = datetime.datetime.now()
  next_hour = next_hour.replace(
    minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)

  delta = next_hour - datetime.datetime.now()
  await asyncio.sleep(delta.total_seconds())

  
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