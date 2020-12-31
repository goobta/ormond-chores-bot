import discord
import dotenv
import pathlib


discord_name = lambda m: m.nick or m.name


def load_env():
  path = pathlib.Path(__file__).resolve().parent.parent / '.env'
  dotenv.load_dotenv(path)


def get_logs_folder():
  return pathlib.Path(__file__).resolve().parent.parent / 'logs/'