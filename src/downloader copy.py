# -*- coding: utf-8 -*-

import os
import re as builtin_re
import json
import shutil
import time
from PIL import Image

from ORM import SQL
import regex_parser_copy as reg
import utils
from bot_stuff import bot
from globals import DIRECTORY, CONFIG, bot

RESULT_DIR = DIRECTORY + CONFIG['results_dir']
QUEUE_DIR = DIRECTORY + CONFIG['queue_name']
LOGFILE = DIRECTORY + CONFIG['downloader_logfile']
CHAT_ID = CONFIG['MAIN_CHAT_ID']

db = SQL(QUEUE_DIR)
l = utils.Log(LOGFILE)

def download_link(link: str):
    # For debugging: if the result dir isn't empty, skip downloading
    if os.listdir(RESULT_DIR):
        l.log("///Skipping dowloading", 1)
        return

    # Run downloading the video
    ytdl_stdout, ytdl_stderr = utils.run_cmd(
        f"""yt-dlp -x {link} \
        --audio-format mp3 --audio-quality 0 --no-part \
        --write-thumbnail --write-description \
        -o "./tmp/%(id)s/%(title)s-%(id)s.%(ext)s" """
    )
    # Removes '[download] ...' lines as they are repeated and flood the logs
    l.log("STDOUT: " + builtin_re.sub(r'\[download\]\s+\d*\.\d% of \d\.\d+.{3} at\s+\d+\.\d+.{3}\/s ETA \d+:\d+\n',
                                    '', ytdl_stdout)
            + "\nSTDERR: " + ytdl_stderr, 1)
    
    # If the stderr of ytdl is not empty, notify the admins:
    if ytdl_stderr:
        utils.notify_admins(f"!youtube-dl has encountered an error, stderr: {ytdl_stderr}")

    # # Download the thumbnail
    # thumb_url = f"https://i.ytimg.com/vi_webp/{link[-11:]}/maxresdefault.webp"
    # thumb_response = requests.get(thumb_url)
    # with open(f"tmp/{link[-11:]}/maxresdefault.webp", "wb") as t:
    #     t.write(thumb_response.content)

    l.log("Downloading finished!", 1)

def prepare_payload(current_link: str, folder, title, uploader):
    """Prepares the payload"""
    os.chdir(folder)
    # Folder + shared basename for all the files in the folder
    fbasename = folder + os.path.splitext(os.listdir()[-1])[0]
    l.log(f"Folder: {folder}, path to .description file: {fbasename + '.description'}", 1)

    if not title:
        title, _ = utils.run_cmd(f'youtube-dl -s -e {current_link}')
    prepared_title = title + '-' + current_link[-11:] + '.description'

    if not uploader:
        uploader = json.loads(utils.run_cmd(f'youtube-dl -s -J {current_link}')[0])['uploader']
    
    with open(fbasename + '.description', 'r') as desc:
        read_track_descr = desc.read()
    
    caption = reg.get_final_caption(prepared_title, read_track_descr)
    # caption = ""
    artist = reg.get_metadata_artist(prepared_title)
    track_name = reg.get_title(prepared_title)

    # Convert to webp thumb to jpg:
    webp_thumb = Image.open(fbasename + '.webp')
    webp_thumb.save(fbasename + '.jpg')

    return (fbasename, caption, artist, track_name)


def send(fbasename: str, caption, artist, track_name):
    with open(fbasename + '.mp3', 'rb') as audio, \
        open(fbasename + '.jpg', 'rb') as thumb:
        with bot:
            os.chdir(DIRECTORY)
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
    l.log(f"==== Running downloading on queue db: {db.name} ====")
    counter = 0
    _empty_check = False
    while True:
        os.chdir(DIRECTORY)
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
             
            download_link(current_link)

            # Path to the folder
            folder = RESULT_DIR + current_link[-11:] + '/'
            send(*prepare_payload(current_link, folder, title, uploader))
            
            cleanup(folder, current_rowid)
            
            counter += 1
            l.log(f"=CYCLE {counter} FINISHED=", 1)

if __name__ == '__main__':
    main()

    #uwu
