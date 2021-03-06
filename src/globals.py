"""Shared variables amongst files."""
import yaml
from pathlib import Path

from pyrogram import Client

DIRECTORY = str(Path(__file__).parent.parent.resolve()) + '/'

CONFIG = yaml.safe_load(open(Path(DIRECTORY).joinpath("config.yml").resolve(), 'r'))

bot = Client("hatebot", CONFIG['API_ID'], CONFIG['API_HASH'], bot_token=CONFIG['TOKEN'])
