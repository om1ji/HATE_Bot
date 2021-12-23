# -*- coding: utf-8 -*-

import os
import re as builtin_re
import json
import shutil
import time
from subprocess import PIPE, check_output, run

from ORM import SQL
import regex_parser as reg
from utils import Log, notify_admins
from bot_stuff import bot
from globals import *

RESULT_DIR = DIRECTION + CONFIG['results_dir']
QUEUE_DIR = DIRECTION + CONFIG['queue_name']
LOGFILE = DIRECTION + CONFIG['downloader_logfile']
CHAT_ID = CONFIG['MAIN_CHAT_ID']

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

def prepare_payload(current_link: str, folder, title, uploader):
    """Prepares the payload"""
    os.chdir(folder)
    # Folder + shared basename for all the files in the folder
    fbasename = folder + os.path.splitext(os.listdir()[0])[0]
    l.log(f"Folder: {folder}, path to .description file: {fbasename + '.description'}", 1)

    with open(fbasename + '.description', 'r') as desc:
        read_track_descr = desc.read()

    with open(fbasename + '.mp3', 'rb') as a:
        audio = a

    with open(fbasename + '.webp', 'rb') as t:
        thumb = t

    if not title:
        title = check_output(f'youtube-dl -s -e {current_link}', shell=True).decode('utf-8').strip()
    prepared_title = title + '-' + current_link[-11:] + '.description'

    if not uploader:
        uploader = json.loads(check_output(f'youtube-dl -s -J {current_link}', shell=True))['uploader']
    
    caption = reg.get_final_caption(prepared_title, read_track_descr)
    artist = reg.get_artist(prepared_title)
    track_name = reg.get_title(prepared_title)

    return (audio, caption, artist, track_name, thumb)

def post_audio(audio, caption, artist, track_name, thumb):
    """Posts audio and logs it"""
    msg = bot.send_audio(
        CHAT_ID,
        audio,
        caption,
        performer=artist,
        title=track_name,
        thumb=thumb
    )
    l.log(f"Audio sent to the main channel! Message id: {msg.message_id}")

def cleanup(folder, current_rowid) -> None:
    """Cleans up artifacts at the end of each cycle."""
    shutil.rmtree(folder)
    l.log(f"Directory {folder} removed", 1)
    db.delete_rowid(current_rowid)
    l.log(f"Row {current_rowid} deleted from the db", 1)

def main() -> None:
    """Entry point and main loop"""
    l.log(f"====Running downloading on queue db: {db.name}====")
    counter = 0
    _empty_check = False
    while True:
        os.chdir(DIRECTION)
        queue = db.fetch_queue()
        # If the queue isn't empty, download the contents
        if not queue:
            if not _empty_check:
                l.log("All cycles finished. Awaiting and polling for the next request...")
                _empty_check = True
            time.sleep(15)
        else:
            _empty_check = False
            current_rowid = db.select_last_rowid()
            current_link = queue[0][0]
            title = queue[0][1]
            uploader = queue[0][2]
            l.log(f"Fetched link: {current_rowid}|{current_link}, running downloading....")

            # Path to the folder
            folder = RESULT_DIR + current_link[-11:] + '/'
            download_link(current_link)
            post_audio(*prepare_payload(current_link, folder, title, uploader))
            cleanup(folder, current_rowid)
            counter += 1
            l.log(f"=CYCLE {counter} FINISHED=", 1)

if __name__ == '__main__':
    main()