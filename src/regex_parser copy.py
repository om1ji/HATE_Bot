import re
import os
import random
from typing import List

import utils
"""
    Важно! Отправлять аргумент в виде открытого и прочитанного файла

"""

#### Compiling regexes
RE_TITLE = re.compile(r"(Title: )(.*)", re.I)
RE_TYPE_PODCAST = re.compile(r'(\d+ Hate Podcast with )(.+)\n|(\d+ Hate Podcast with )(.+) \n', re.I)
RE_TYPE_REGULAR = re.compile(r'(Artists?: |Title: |Label: |Genre: )', re.I)
RE_SOUNDCLOUD = re.compile(r'Download.+:\n.+', re.I)
RE_ARTIST = re.compile(r"(.+)(?: ?- )")
RE_REMIX = re.compile(r"(?<=\()(.+)(?= Remix\))|(?<=\()(.+)(?= Edit\))")
_RE_YT_LINK = r'[a-zA-Z0-9_\-]{11}\.\.?description)$'

"""
    ОЧЕНЬ ВАЖНО!! В аргумент функций artist, title и orig_link подаётся НАЗВАНИЕ описания, а не его содержимое
"""

def get_album_title(desc: str) -> str:
   ...

def get_upload_type(desc: str) -> int:
    ...

def get_podcast_info(desc: str) -> str:
    ...

def get_artist(name: str) -> str:
    ...

def get_title(name: str) -> str:
    ...

def get_orig_link(name: str) -> str:
    ...

def get_label(desc: str) -> str:
    ...

def get_catalogue(name: str) -> str:
    ...

def get_style(desc: str) -> str:
    ...

def get_support_links(desc: str) -> str:
    ...

def hash_artist(artist: str) -> str:
    ...

def get_final_caption(descr_name: str, descr_contents: str, debug_toggle=0) -> str:
    """
        Get final post caption
        :param descr_name: name of description file
        :param descr_contents: description contents
        :param debug_toggle: (default = 0) debug toggle for song name
    """
    ...


def get_metadata(description: str) -> List:
    return [
        get_artist(description),
        get_title(description),
        get_catalogue(description)
    ]

def _tests() -> None:
    """
        тестики от артеметры, не трогать
    """
    name = "Ancient Methods - In Silence Die Selektion (In Stille Remix) [PS09]-nLHzYaELlRs.description"
    with open("D:\\test\\desc\\descriptions\\" + name, "r", encoding="utf-8") as f:
        fin_prep = f.read()
    
    # dir_list = os.listdir("D:\\test\\desc\\descriptions\\")
    # name = dir_list[random.randint(0, 656)]
    # description = open("D:\\test\\desc\\descriptions\\" + name, "r", encoding="utf-8")
    # print("\n" + name)

    print("\n" + get_final_caption(name, fin_prep, 1) + "\n")



if __name__ == '__main__':
    _tests()



"""
    ТУДУШКА:

    1) сделать чтобы работали эти и тестить ещё:

        Radical G - The Deserted Kingdom (Parallx Cold Eyes Mix) [RR5]-HjS6WVHiN4s.description

        Radical G - The Deserted Kingdom (10 Inch Version) [RR5]-msQyuGdUx4Y.description


"""


