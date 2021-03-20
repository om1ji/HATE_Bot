import telebot, requests
import os, json, time
import regex

TOKEN = '1591601193:AAHWLplYpkAPwbwq7c-0A51169BQpf9N04s'
CHAT_ID = -1001389676477
bot = telebot.TeleBot(TOKEN)

direction = r'/home/pi/Desktop/HATE/Tracks'

# Инициализация файлов в директории
def init():
    return os.listdir(direction)

# Местонахождение аудиофайла
file_path_in = direction + '\\' + init()[1]

# Местонахождение описания
description = direction + '\\' + init()[0]

# ------------------------------------------------------------------------ #

@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(CHAT_ID, 'Бот запущен. Инициализация Cum...')
 
while init() != False:

    descr = open(description, 'r')
    descr = descr.read()

    print('Начинаем отправку...\n')

    single_file = {'audio': open(file_path_in, 'rb')}

    the_file = requests.post("https://api.telegram.org/bot1591601193:AAHWLplYpkAPwbwq7c-0A51169BQpf9N04s/sendAudio?chat_id=-1001170446896", files=single_file)
    print(the_file.content)

    file_id = json.loads(the_file.text)['result']['audio']['file_id']
    message_id = json.loads(the_file.text)['result']['message_id']

    file_path = bot.get_file(file_id).file_path
    file_itself = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_path))

    bot.send_audio(CHAT_ID, audio=file_itself.content, caption=regex.final(descr), performer=regex.artist(descr), title=regex.title(descr))

    close_file = single_file['audio']
    close_file.close()

    bot.delete_message(-1001170446896, message_id)
    os.remove(file_path_in)
    os.remove(description)

    print('Файл отправлен!')
    continue

if __name__=='__main__':
    bot.polling()