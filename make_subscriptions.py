from typing import Container 
from requests import post
from time import sleep


url = ["UC6qQOTx9LuKMC5p2dbjmSRg","UCLXM6lFu1s7MjInzUk5bfNA"]
while True:
    for i in url:
        r = post(f'https://pubsubhubbub.appspot.com/subscribe?hub.callback=http://om1ji.site:8080/webhook&hub.mode=subscribe&hub.topic=https://www.youtube.com/xml/feeds/videos.xml?channel_id={i}')
        print(r.status_code)
    print('Wait 6 days')
    sleep(518400)
