from requests import get

channels = ["UC6qQOTx9LuKMC5p2dbjmSRg", "UCLXM6lFu1s7MjInzUk5bfNA"]

for i in channels:
    print(get(f'https://pubsubhubbub.appspot.com/subscribe?hub.callback=http://92.255.109.78:7777/webhook&hub.mode=subscribe&hub.topic=https://www.youtube.com/xml/feeds/videos.xml?channel_id={i}'))
