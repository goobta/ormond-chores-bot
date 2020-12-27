import dotenv
import pathlib


def load_env():
  path = pathlib.Path(__file__).resolve().parent.parent / '.env'
  dotenv.load_dotenv(path)