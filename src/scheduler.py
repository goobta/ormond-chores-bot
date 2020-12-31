from dis import dis, disco
from typing import List, Text, Tuple

import calendar
import datetime
import discord
import logging
import pytablewriter

import util


class Scheduler:
  RESET_TIME = datetime.time(4, 20, 0, 0)
  NOTIFICATION_START = datetime.time(21, 30, 0, 0)
  
  def __init__(self, guild: discord.Guild, channel: discord.ChannelType, 
               users: List[discord.Member], logger_name='discord'):
    self.guild = guild
    self.notification_channel = channel

    self.signed_off = False
    self._users = users
    self._logger = logging.getLogger(logger_name)

  @property
  def on_call(self) -> discord.Member:
    return self._users[0]

  def generate_schedule(self) -> Text:
    dow = datetime.datetime.today().weekday()

    if not self.signed_off:
      days = ['{} (today)'.format(calendar.day_abbr[dow])]
    else:
      days = ['{} (tmrw)'.format(calendar.day_abbr[dow + 1])]
    people = [util.discord_name(self._users[0])]

    for i in range(1, 7):
      if not self._signed_off:
        day_name = calendar.day_abbr[(dow + i) % 7]
      else:
        day_name = calendar.day_abbr[(dow + i + 1) % 7]
      days.append(day_name)

      user = self._users[i % len(self._users)]
      people.append(user.nick or user.name)

    writer = pytablewriter.MarkdownTableWriter(
      headers=days, value_matrix=[people])

    return writer.dumps()

  def swap(self, mem1: discord.Member, mem2: discord.Member):
    if mem1 == mem2:
      raise ValueError('Members need to be different.')

    mem1_idx = self._users.index(mem1)
    mem2_idx = self._users.index(mem2)

    self._users[mem1_idx] = mem2
    self._users[mem2_idx] = mem1

  def signoff(self):
    self._users.append(self._users.pop(0))
    self.signed_off = True