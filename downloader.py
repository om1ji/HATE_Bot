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
RESULT_DIR = CONFIG['results_dir']
QUEUE_DIR = DIRECTION + CONFIG['queue_name']
LOGFILE = DIRECTION + CONFIG['downloader_logfile']
TOKEN = CONFIG['TOKEN']
CHAT_ID = CONFIG['MAIN_CHAT_ID']
TMP_CHAT_ID = CONFIG['TEMP_CHAT_ID']
ADMINS = CONFIG['ADMINS']
BOT = telebot.TeleBot(TOKEN)

def download_from_queue(QUEUE_DIR):
    _log(LOGFILE, "====Running downloading on queue db: " + QUEUE_DIR + "====")
    _con = sqlite3.connect(QUEUE_DIR)
    cur = _con.cursor() 
    counter = 0
    empty_check = False
    while True:
        os.chdir(DIRECTION)
        current_link = db_retry_until_unlocked(LOGFILE, QUEUE_DIR, "SELECT * FROM queue;")
        if current_link:
            current_link = current_link[0][0]
            current_rowid = db_retry_until_unlocked(LOGFILE, QUEUE_DIR, """SELECT rowid FROM queue;""")[0][0]
            
            empty_check = False
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
            _log(LOGFILE, "STDOUT: " + re.sub(r'\[download\]\s+\d+\.\d% of \d\.\d+.{3} at\s+\d+\.\d+.{3}\/s ETA \d+:\d+\n',
                                               '', ytdl_stdout)
                      + "\nSTDERR: " + ytdl_stderr, 1)
            if ytdl_stderr:
                for admin in ADMINS:
                    BOT.send_message(admin, f"!youtube-dl has encountered an error, stderr: {ytdl_stderr}")
            _log(LOGFILE, "Downloading finished!", 1)
            folder = RESULT_DIR + current_link[-11:] + '/' #Путь до папки
            os.chdir(folder)
            basename = os.path.splitext(os.listdir()[0])[0]

            track_descr_path = folder + basename + '.description' #Путь до файла .description
            track_descr = open(track_descr_path)
            read_track_descr = track_descr.read()

            _log(LOGFILE, f"Folder: {folder}, path to .description file: {track_descr_path}", 1)
            single_file = {'document': open(folder + basename + '.mp3', 'rb')}

            try:
                thumb_conv = Image.open(folder + basename + '.webp')
                thumb_conv.save(folder + basename + '.jpg', 'jpeg')
                thumbnail = {'document': open(folder + basename + '.jpg', 'rb')}
            except FileNotFoundError:
                try:
                    thumb_conv = Image.open(folder + basename + '.jpg')
                    thumbnail = {'document': open(folder + basename + '.jpg', 'rb')}
                except FileNotFoundError:
                    _log("!!!!!Thumbnail did not download properly, using black pic")
            

            _log(LOGFILE, "Sending to temp channel...", 1)
            the_file = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument?chat_id={TMP_CHAT_ID}", files=single_file)
            # BOT.send_audio(CHAT_ID, audio=single_file.content)
            the_thumb = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument?chat_id={TMP_CHAT_ID}", files=thumbnail)
            

            try:
                _log(LOGFILE, "Result: " + str(json.loads(the_file.text)), 1)
                file_id = json.loads(the_file.text)['result']['audio']['file_id']
            except KeyError:
                file_id = json.loads(the_file.text)['result']['document']['file_id']
            
            duration = str(check_output(f'youtube-dl -s --get-duration {current_link}', shell=True))[2:6]
            duration = sum(x * int(t) for x, t in zip([60, 1], duration.split(":"))) 
            _log(LOGFILE, "Duration: " + str(duration), 1)

            message_id = json.loads(the_file.text)['result']['message_id']
            _log(LOGFILE, "thumb result: " + str(json.loads(the_thumb.text)['result']), 1)
            thumb_id = json.loads(the_thumb.text)['result']['document']['file_id']

            file_path = BOT.get_file(file_id).file_path
            _log(LOGFILE, f"File path: {file_path}; File id: {file_id}; Message id: {message_id}", 2)
            file_itself = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_path}')

            channel_name = json.loads(check_output(f'youtube-dl -s -J {current_link}', shell=True))['uploader']
            if channel_name == 'HATE LAB':
                caption = get_final_caption(basename + '.description', read_track_descr) + '\n' + '#HATE_LAB'
            else: 
                caption = get_final_caption(basename + '.description', read_track_descr)

            _log(LOGFILE, f"Caption: {caption}", 2)
            BOT.send_audio(CHAT_ID, audio=file_itself.content, 
                                    caption=caption, 
                                    performer=get_artist(basename + '.description'), 
                                    title=get_title(basename + '.description'),
                                    thumb=thumb_id,
                                    duration=duration,
                                    parse_mode='HTML')
            _log(LOGFILE, "Audio sent to the main channel!")

            track_descr.close()
            single_file['document'].close()

            # BOT.delete_message(TMP_CHAT_ID, message_id)
            # _log(LOGFILE, "Message deleted from temp channel", 1)
            shutil.rmtree(folder)
            _log(LOGFILE, f"Directory {folder} removed", 1)

            db_retry_until_unlocked(LOGFILE, QUEUE_DIR, f"""DELETE FROM queue
                                                            WHERE rowid={current_rowid};
                                                            """)

            _con.commit()
            _log(LOGFILE, f"Row {current_rowid} deleted from the db", 1)
            counter += 1
            _log(LOGFILE, f"=CYCLE {counter} FINISHED=" , 1)
        else:
            if not empty_check:
                _log(LOGFILE, "All cycles finished. Awaiting and polling for the next request...")
                empty_check = True
            time.sleep(15)

if __name__ == '__main__':
    download_from_queue(QUEUE_DIR)
