# -*- coding: utf-8 -*-

import os
import re as builtin_re
import shutil
import json
import time
import requests
from subprocess import PIPE, check_output, run
import yaml
from io import BufferedReader, TextIOWrapper # for parameter types

from pyrogram import Client, filters

from ORM import SQL
import regex
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
    # Run downloading
    ytdl_result = run(f"""youtube-dl -x {link} \
                          --audio-format mp3 --audio-quality 0 --no-part \
                          --write-description -o "./tmp/%(id)s/%(title)s-%(id)s.%(ext)s" """, 
                          shell = True, 
                          stdout=PIPE,
                          stderr=PIPE)
    
    ytdl_stdout = ytdl_result.stdout.decode('utf-8').strip()
    ytdl_stderr = ytdl_result.stderr.decode('utf-8').strip()
    # Removes '[download] ...' lines as they are repeated and flood the logs
    l.log("STDOUT: " + builtin_re.sub(r'\[download\]\s+\d*\.\d% of \d\.\d+.{3} at\s+\d+\.\d+.{3}\/s ETA \d+:\d+\n',
                                       '', ytdl_stdout)
              + "\nSTDERR: " + ytdl_stderr, 1)
    # If the stderr of ytdl is not empty, notify the admins: 
    if ytdl_stderr:
        notify_admins(f"!youtube-dl has encountered an error, stderr: {ytdl_stderr}")
    
    
    l.log("Downloading finished!", 1)

async def prepare_and_send(current_link: str):
    folder = RESULT_DIR + current_link[-11:] + '/' # Path to the folder
    os.chdir(folder)
    # Folder + shared basename for all the files in the folder
    fbasename = folder + os.path.splitext(os.listdir()[0])[0]
    # Description file:
    with open(fbasename + '.description', 'r') as desc:
        read_track_descr = desc.read() 

    l.log(f"Folder: {folder}, path to .description file: {fbasename + '.description'}", 1)
    
    with open(fbasename + '.mp3', 'rb') as a:
        audio = a

    # TODO fix depending on youtube-dl for info that can be obtained
    # directly from the webhook payload     
    orig_video_title = check_output(f'youtube-dl -s -e {current_link}', shell=True).decode('utf-8').strip()
    prepared_title = orig_video_title + '-' + current_link[-11:] + '.description'
    caption = regex.get_final_caption(prepared_title, read_track_descr)
    
    duration = str(check_output(f'youtube-dl -s --get-duration {current_link}', shell=True))[2:6]
    duration = sum(x * int(t) for x, t in zip([60, 1], duration.split(":"))) 
    
    msg = await BOT.send_audio(
        CHAT_ID, 
        audio, 
        caption,
        performer=regex.get_artist(prepared_title),
        title=regex.get_title(prepared_title),
        thumb=regex.get_thumbnail(current_link),
        duration=duration
    )
    l.log(f"Audio sent to the main channel! Message id: {msg.message_id}")

async def post_audio(audio, caption, artist, title, thumb, duration):
    ...

def download_from_queue() -> None:
    l.log(f"====Running downloading on queue db: {db.name}====")
    counter = 0
    _empty_check = False
    while True:
        os.chdir(DIRECTION)
        current_link = db.fetch_queue()
        # If the queue isn't empty, download the contents
        if not current_link:
            if not _empty_check:
                l.log("All cycles finished. Awaiting and polling for the next request...")
                _empty_check = True
            time.sleep(15)
        else:
            _empty_check = False
            current_rowid = db.select_last_rowid()
            current_link = current_link[0][0]
            
            l.log(f"Fetched link: {current_rowid}|{current_link}, running downloading....")
            
            download_link(current_link)

