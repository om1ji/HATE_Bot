import telebot
from telebot import types
import sqlite3
import requests
import os
import yaml

DIRECTION = r'/home/bot/HATE/'
CONFIG = yaml.safe_load(open(DIRECTION + 'config.yml', 'r'))
TOKEN = CONFIG['TOKEN']
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):

    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        FOREIGN KEY (id)
            REFERENCES yt_ch (id)
        FOREIGN KEY (yt_ch)
            REFERENCES tg_ch (yt_ch)
        );""")
    connect.commit()

    bot.send_message(message.chat.id, 'Приветствую!')
    people_id = message.chat.id

    cursor.execute(f"SELECT id FROM users WHERE id = {people_id};")
    data = cursor.fetchone()

    if data is None:
        user_id = message.chat.id
        print(type(user_id))
        cursor.execute("INSERT INTO users (id) VALUES(?);", user_id)
        connect.commit()
    else:
        print('Пользователь ' + message.chat.username + ' повторно зарегался')

@bot.message_handler(commands=['/subscribe'])
def subscribe(message):

    bot.send_message(message.chat.id, 'Отправь ссылку на Ютуб канал')
#     bot.register_next_step_handler_by_chat_id(message.chat.id, subscribe_pubsub)


# def subscribe_pubsub(message):
#     people_id = message.chat.id
    
#     cursor.execute(f"""SELECT yt_ch FROM users WHERE id = {people_id}""")
#     data = cursor.fetchone()
#     if data is None:
#         url = message.text
#         ch_id = os.system(f'youtube-dl -s {url} -j')
#         print(ch_id)

#     r = requests.post(f"""https://pubsubhubbub.appspot.com/subscribe?
#                         hub.callback=http://om1ji.site/webhook&
#                         hub.mode=subscribe&
#                         hub.topic=https://www.youtube.com/xml/feeds/videos.xml?channel_id={ch_id}""")
#     if r.ok:
#         cursor.execute(f"INSERT INTO users (yt_ch) VALUES(?);", ch_id)
#         connect.commit()

#     bot.send_message(message.chat.id, 'Успешная подписка на <a href="{ch_url}">канал</a>!', parse_mode='HTML')

if __name__=='__main__':
    connect = sqlite3.connect('users.db')
    bot.polling()