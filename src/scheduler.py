from typing import List

import datetime
import discord
import logging


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