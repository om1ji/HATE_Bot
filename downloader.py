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

import telebot

from regex import *
from utils import _log, db_retry_until_unlocked as dbret, notify_admins

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
SKIP_IF_OVER_20MB = CONFIG['skip_if_over_20mb']
API = 'https://api.telegram.org/'

def download_from_queue(QUEUE_DIR: str) -> None:
    _log(LOGFILE, "====Running downloading on queue db: " + QUEUE_DIR + "====")
    counter = 0
    _empty_check = False
    while True:
        os.chdir(DIRECTION)
        current_link = dbret(LOGFILE, QUEUE_DIR, "SELECT * FROM queue;")
        # If the queue isn't empty, download the contents
        if current_link:
            _empty_check = False
            current_link = current_link[0][0]
            current_rowid = dbret(LOGFILE, QUEUE_DIR, """SELECT rowid FROM queue;""")[0][0]
            
            _log(LOGFILE, f"Fetched link: {current_rowid}|{current_link}, running downloading....")
            # Run downloading
            ytdl_result = run(f"""youtube-dl -x {current_link} \
                                  --audio-format mp3 --audio-quality 0 --no-part \
                                  --write-description -o "./tmp/%(id)s/%(title)s-%(id)s.%(ext)s" """, 
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
                notify_admins(f"!youtube-dl has encountered an error, stderr: {ytdl_stderr}")

            
            _log(LOGFILE, "Downloading finished!", 1)

                
            folder = RESULT_DIR + current_link[-11:] + '/' # Path to the folder
            os.chdir(folder)
            # Folder + shared basename for all the files in the folder
            fbasename = folder + os.path.splitext(os.listdir()[0])[0]
            # Description file:
            track_descr = open(fbasename + '.description')
            read_track_descr = track_descr.read() 

            _log(LOGFILE, f"Folder: {folder}, path to .description file: {fbasename + '.description'}", 1)
            
            audio_document = {'document': open(fbasename + '.mp3', 'rb')}

            # Gets file size in mb
            audio_size = os.path.getsize(fbasename + '.mp3')/1e+6
            if audio_size > 20:
                if SKIP_IF_OVER_20MB:
                    notify_admins(f"Skipped sending \"{fbasename[31:]}\" because it is over 20 MB ({audio_size}).")
                    finish_cycle(track_descr, audio_document, folder, current_rowid, counter)
                else:
                    handle_manual_upload(fbasename, audio_size)
            else:
                # Send to temporary channel 
                _log(LOGFILE, "Sending to temp channel...", 1)
                posted_audio = requests.post(f"{API}bot{TOKEN}/sendDocument?chat_id={TMP_CHAT_ID}", files=audio_document)
            
            message_id = json.loads(posted_audio.text)['result']['message_id']

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

            _log(LOGFILE, f"Caption: {caption}", 2)
            
            #Sends the file
            BOT.send_audio(CHAT_ID, audio=audio_from_temp.content, 
                                    caption=caption, 
                                    performer=get_artist(prepared_title), 
                                    title=get_title(prepared_title),
                                    thumb=get_thumbnail(current_link),
                                    duration=duration,
                                    parse_mode='HTML')
            _log(LOGFILE, "Audio sent to the main channel!")
            
            finish_cycle(track_descr, audio_document, folder, current_rowid, counter)

        else:
            if not _empty_check:
                _log(LOGFILE, "All cycles finished. Awaiting and polling for the next request...")
                _empty_check = True
            time.sleep(15)

def handle_manual_upload(fbasename, audio_size):
    """
        PLZ write docs so i could understand what you want. ='( artemetra
    """
    BOT.send_message(TMP_CHAT_ID, "Send the audio in the next message:")
    notify_admins( f"""
                    File \"{fbasename[31:]}\" is {audio_size} MB in size. 
                    Please send the audio file to the temporary channel under \
                    bot's message.""")
    resulted_json = '' # This line is just a placeholder, feature not implemented yet
    _log(LOGFILE, f"Received JSON from manual upload: {resulted_json}", 2)
    notify_admins(f"Successfully got audio data! Continuing as usual...")
    return resulted_json


def finish_cycle(track_descr: TextIOWrapper, 
                audio_document: dict[str, BufferedReader], 
                folder, current_rowid, counter):
        
        track_descr.close()
        audio_document['document'].close()

        # BOT.delete_message(TMP_CHAT_ID, message_id)
        # _log(LOGFILE, "Message deleted from temp channel", 1)
        shutil.rmtree(folder)
        _log(LOGFILE, f"Directory {folder} removed", 1)

        dbret(LOGFILE, QUEUE_DIR, f"""
                                   DELETE FROM queue
                                   WHERE rowid={current_rowid};
                                   """)

        _log(LOGFILE, f"Row {current_rowid} deleted from the db", 1)
        counter += 1
        _log(LOGFILE, f"=CYCLE {counter} FINISHED=" , 1)

if __name__ == '__main__':
    download_from_queue(QUEUE_DIR)

# TODO if file > 20 mb: handle...() 