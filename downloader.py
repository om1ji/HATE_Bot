# -*- coding: utf-8 -*-

import os
import shutil
import json
import sqlite3
import time
import requests
from subprocess import PIPE, check_output, run
import yaml

import telebot
from PIL import Image

from regex import *
from utils import _log, db_retry_until_unlocked

DIRECTION = r'/home/bot/HATE/'
CONFIG = yaml.safe_load(open(DIRECTION + 'config.yml', 'r'))
RESULT_DIR = DIRECTION + CONFIG['results_dir']
QUEUE_DIR = DIRECTION + CONFIG['queue_name']
LOGFILE = DIRECTION + CONFIG['downloader_logfile']
TOKEN = CONFIG['TOKEN']
BOT = telebot.TeleBot(TOKEN)
CHAT_ID = CONFIG['MAIN_CHAT_ID']
TMP_CHAT_ID = CONFIG['TEMP_CHAT_ID']
ADMINS = CONFIG['ADMINS']
API = 'https://api.telegram.org'

def download_from_queue(QUEUE_DIR: str) -> None:
    _log(LOGFILE, "====Running downloading on queue db: " + QUEUE_DIR + "====")
    counter = 0
    _empty_check = False
    while True:
        os.chdir(DIRECTION)
        current_link = db_retry_until_unlocked(LOGFILE, QUEUE_DIR, "SELECT * FROM queue;")
        # If the queue isn't empty, download the contents
        if current_link:
            _empty_check = False
            current_link = current_link[0][0]
            current_rowid = db_retry_until_unlocked(LOGFILE, QUEUE_DIR, """SELECT rowid FROM queue;""")[0][0]
            
            _log(LOGFILE, f"Fetched link: {current_rowid}|{current_link}, running downloading....")
            # Run downloading
            ytdl_result = run(f"""youtube-dl -x {current_link} \
                                  --audio-format mp3 --audio-quality 0 --no-part \
                                  --write-description -o "./tmp/%(id)s/%(title)s-%(id)s.%(ext)s" \
                                  --write-thumbnail""", 
                                  shell = True, 
                                  stdout=PIPE,
                                  stderr=PIPE)
            
            ytdl_stdout = ytdl_result.stdout.decode('utf-8').strip()
            ytdl_stderr = ytdl_result.stderr.decode('utf-8').strip()
            # Removes '[download] ...' lines as they are repeated and flood the logs
            _log(LOGFILE, "STDOUT: " + re.sub(r'\[download\]\s+\d*\.\d% of \d\.\d+.{3} at\s+\d+\.\d+.{3}\/s ETA \d+:\d+\n',
                                               '', ytdl_stdout)
                      + "\nSTDERR: " + ytdl_stderr, 1)
            # If the stderr of ytdl is not empty, notify the admins: 
            if ytdl_stderr:
                for admin in ADMINS:
                    BOT.send_message(admin, f"!youtube-dl has encountered an error, stderr: {ytdl_stderr}")
            
            _log(LOGFILE, "Downloading finished!", 1)
            folder = RESULT_DIR + current_link[-11:] + '/' # Path to the folder
            os.chdir(folder)
            # Folder + shared basename for all the files in the folder
            fbasename = folder + os.path.splitext(os.listdir()[0])[0]
            # Description file:
            track_descr = open(fbasename + '.description')
            read_track_descr = track_descr.read() 

            _log(LOGFILE, f"Folder: {folder}, path to .description file: {fbasename + '.description'}", 1)
            
            # Try to convert webp thumb to jpg 
            try:
                Image.open(fbasename + '.webp').save(fbasename + '.jpg', 'jpeg')
                thumbnail = {'document': open(fbasename + '.jpg', 'rb')}
            except FileNotFoundError:
                try:
                    thumbnail = {'document': open(fbasename + '.jpg', 'rb')}
                except FileNotFoundError:
                    _log("!!!!!Thumbnail did not download properly, using black pic")
            
            audio_document = {'document': open(fbasename + '.mp3', 'rb')}

            # Send to temporary channel
            _log(LOGFILE, "Sending to temp channel...", 1)
            posted_audio = requests.post(f"{API}{TOKEN}/sendDocument?chat_id={TMP_CHAT_ID}", files=audio_document)
            posted_thumb = requests.post(f"{API}{TOKEN}/sendDocument?chat_id={TMP_CHAT_ID}", files=thumbnail)

            message_id = json.loads(posted_audio.text)['result']['message_id']
            thumb_id = json.loads(posted_thumb.text)['result']['document']['file_id']
            _log(LOGFILE, "thumb result: " + str(json.loads(posted_thumb.text)['result']), 1)

            try:
                _log(LOGFILE, "Result: " + str(json.loads(posted_audio.text)), 1)
                file_id = json.loads(posted_audio.text)['result']['audio']['file_id']
            except KeyError:
                file_id = json.loads(posted_audio.text)['result']['document']['file_id']
            

            file_path = BOT.get_file(file_id).file_path
            _log(LOGFILE, f"File path: {file_path}; File id: {file_id}; Message id: {message_id}", 2)
            audio_from_temp = requests.get(f'{API}/file/bot{TOKEN}/{file_path}')

            # Calculate duration of the track
            duration = str(check_output(f'youtube-dl -s --get-duration {current_link}', shell=True))[2:6]
            duration = sum(x * int(t) for x, t in zip([60, 1], duration.split(":"))) 
            _log(LOGFILE, f"Duration: {duration}", 1)

            # Get original video title to preserve characters that aren't allowed
            # in file names and thus were excluded by youtube-dl
            orig_video_title = check_output(f'youtube-dl -s -e {current_link}', shell=True).decode('utf-8').strip()
            prepared_title = orig_video_title + '-' + current_link[-11:] + '.description'
            
            channel_name = json.loads(check_output(f'youtube-dl -s -J {current_link}', shell=True))['uploader']
            if channel_name == 'HATE LAB':
                caption = get_final_caption(prepared_title, read_track_descr) + '\n' + '#HATE_LAB'
            else: 
                caption = get_final_caption(prepared_title, read_track_descr)

            _log(LOGFILE, f"Caption: {caption.replace('\n', '\\n')}", 2)

            
            #Sends the file. Простите, мне нужно что то коммитнуть для статистики 👉👈
            
            BOT.send_audio(CHAT_ID, audio=audio_from_temp.content, 
                                    caption=caption, 
                                    performer=get_artist(prepared_title), 
                                    title=get_title(prepared_title),
                                    thumb=thumb_id,
                                    duration=duration,
                                    parse_mode='HTML')
            _log(LOGFILE, "Audio sent to the main channel!")

            finish_cycle(track_descr, audio_document, folder, current_rowid, counter)

        else:
            if not _empty_check:
                _log(LOGFILE, "All cycles finished. Awaiting and polling for the next request...")
                _empty_check = True
            time.sleep(15)

def finish_cycle(track_descr, single_file, folder, current_rowid, counter):
        track_descr.close()
        single_file['document'].close()

        # BOT.delete_message(TMP_CHAT_ID, message_id)
        # _log(LOGFILE, "Message deleted from temp channel", 1)
        shutil.rmtree(folder)
        _log(LOGFILE, f"Directory {folder} removed", 1)

        db_retry_until_unlocked(LOGFILE, QUEUE_DIR, f"""DELETE FROM queue
                                                        WHERE rowid={current_rowid};
                                                        """)

        _log(LOGFILE, f"Row {current_rowid} deleted from the db", 1)
        counter += 1
        _log(LOGFILE, f"=CYCLE {counter} FINISHED=" , 1)


if __name__ == '__main__':
    download_from_queue(QUEUE_DIR)
