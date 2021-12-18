# -*- coding: utf-8 -*-

import os
import re
import shutil
import json
import time
import requests
from subprocess import PIPE, check_output, run
import yaml
from io import BufferedReader, TextIOWrapper # for parameter types

from pyrogram import Client, filters

from ORM import SQL
import regex as reg
from utils import Log, db_retry_until_unlocked as dbret, notify_admins

DIRECTION = r'/home/bot/HATE/'
CONFIG = yaml.safe_load(open(DIRECTION + 'config.yml', 'r'))
RESULT_DIR = DIRECTION + CONFIG['results_dir']
QUEUE_DIR = DIRECTION + CONFIG['queue_name']
LOGFILE = DIRECTION + CONFIG['downloader_logfile']
TOKEN = CONFIG['TOKEN']
BOT = Client("hatebot", CONFIG['API_ID'], CONFIG['API_HASH'], bot_token=TOKEN)
CHAT_ID = CONFIG['MAIN_CHAT_ID']
TMP_CHAT_ID = CONFIG['TEMP_CHAT_ID']
ADMINS = CONFIG['ADMINS']
API = 'https://api.telegram.org/'

db = SQL(QUEUE_DIR)
l = Log(LOGFILE)
def download_link(link: str):
    ...


def download_from_queue() -> None:
    l.log(LOGFILE, f"====Running downloading on queue db: {db.name}====")
    counter = 0
    _empty_check = False
    while True:
        os.chdir(DIRECTION)
        current_link = db.fetch_queue()
        # If the queue isn't empty, download the contents
        if not current_link:
            if not _empty_check:
                l.log(LOGFILE, "All cycles finished. Awaiting and polling for the next request...")
                _empty_check = True
            time.sleep(15)
        else:
            _empty_check = False
            current_rowid = db.select_last_rowid()
            current_link = current_link[0][0]
            
            download_link(current_link[0][0])
