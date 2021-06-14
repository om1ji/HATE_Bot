import requests

data = """<entry>
  <id>yt:video:gpmTmP15tzk</id>
  <yt:videoId>gpmTmP15tzk</yt:videoId>
  <yt:channelId>UC6qQOTx9LuKMC5p2dbjmSRg</yt:channelId>
  <title>Foreign Material - Into the Gleams of Forgetfulness [OB.M07]</title>
  <link rel="alternate" href="https://www.youtube.com/watch?v=gpmTmP15tzk"/>
  <author>
   <name>HATE</name>
   <uri>https://www.youtube.com/channel/UC6qQOTx9LuKMC5p2dbjmSRg</uri>
  </author>
  <published>2021-03-22T08:07:30+00:00</published>
  <updated>2021-03-22T08:08:34.880816992+00:00</updated>
 </entry>"""

# r = requests.post('http://127.0.0.1:5000/webhook', data=data)
r = requests.post('http://195.182.203.207/webhook', data=data)
print(r)