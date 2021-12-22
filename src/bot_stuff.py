import yaml

from pyrogram import Client, filters

DIRECTION = r'/home/bot/HATE/'
CONFIG = yaml.safe_load(open(DIRECTION + 'config.yml', 'r'))
app = Client("hatebot", CONFIG['API_ID'], CONFIG['API_HASH'], bot_token=CONFIG['TOKEN'])