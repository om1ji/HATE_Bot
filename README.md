# Телеграм бот для автоматической загрузки аудиофайлов с видеохостинга YouTube.

Алгоритм Телеграм бота основан на технологии [webhook](https://ru.wikipedia.org/wiki/Webhook)

## Для работы бота нужно:

1. Иметь [белый](https://help.keenetic.com/hc/ru/articles/213965789-%D0%92-%D1%87%D0%B5%D0%BC-%D0%BE%D1%82%D0%BB%D0%B8%D1%87%D0%B8%D0%B5-%D0%B1%D0%B5%D0%BB%D0%BE%D0%B3%D0%BE-%D0%B8-%D1%81%D0%B5%D1%80%D0%BE%D0%B3%D0%BE-IP-%D0%B0%D0%B4%D1%80%D0%B5%D1%81%D0%B0-) IP.

2. Иметь либо VPS, либо домашний сервер (можно любое устройство, поддерживающее Linux или Windows) с бесперебойной работой и постоянным подключением к интернету.

3. Установить все зависимости: ```pip install -r requitements.txt```
    - Если Linux, то ```pip3```

4. Запуск бота:
    - Linux: ```sudo FLASK_APP=server_linux.py flask run --host=0.0.0.0 --port=80```
    - Windows: ```set FLASK_APP=server_windows.py flask run --host=0.0.0.0 --port=80```

5. Подписаться на уведомления PubSubHubbub:
    - Либо через [сайт](https://pubsubhubbub.appspot.com/subscribe).
    - Либо через HTTP POST-запрос:
``` 
https://pubsubhubbub.appspot.com/subscribe?hub.callback={URL до вашего сервера}&hub.mode=subscribe&hub.topic=https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCMSVWxNp1lkEGpDClzm8Qvw
```
