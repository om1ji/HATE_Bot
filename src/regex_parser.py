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

#Берёт автора с самого релиза/альбома. Скорее всего уберу:

#def artist(desc):
#    #Artist
#    artist_raw = re.search(r"(Artists?: )(.*)", desc)
#    artist = artist_raw.group(2).strip()
#    return artist

#Берёт название с самого релиза/альбома, для метаданных

def get_album_title(desc: str) -> str:
   #Title
   title_raw = re.search(RE_TITLE, desc)
   title = title_raw.group(2).strip()
   return title

"""
    ОЧЕНЬ ВАЖНО!! В аргумент функций artist, title и orig_link подаётся НАЗВАНИЕ описания, а не его содержимое
"""

def get_upload_type(desc: str) -> int:
    """
    Returns the upload type of the video:
    1 - regular release
    2 - podcast
    3 - special/other/unmathed
    """
    _type_raw = re.search(RE_TYPE_PODCAST, desc)
    if _type_raw != None:
        return 2
    else:
        _type_raw = re.search(RE_TYPE_REGULAR, desc)
        if _type_raw != None:
            return 1
        else:
            return 3


def get_podcast_info(desc: str) -> str:
    _podcast_descr_raw = re.search(RE_TYPE_PODCAST, desc)
    _podcast_descr = _podcast_descr_raw.group(1).strip()
    _podcast_author = _podcast_descr_raw.group(2).strip()
    _soundcloud = re.search(RE_SOUNDCLOUD, desc).group(0).strip()

    _podcast_author = re.sub(r'[\[\]\(\)\.]', '', _podcast_author)
    _podcast_author = _podcast_author.replace(' ', '_')
    _podcast_author = '#' + _podcast_author

    return _podcast_descr, _podcast_author, _soundcloud

def get_artist(name: str) -> str:
    #Artist
    artist_raw = re.search(RE_ARTIST, name)
    if artist_raw == None:
        utils.notify_admins(f"Something went wrong in parsing the artist! Raw = {artist_raw}, using \"Unknown\" as artist ")
        return "Unknown"
    artist = artist_raw.group(1).strip()

    remixer_raw = re.search(RE_REMIX, name, re.IGNORECASE)
    if remixer_raw == None:
        remixer = ""
    else:
        remixer = " & " + str(remixer_raw.group(1)).strip() + str(remixer_raw.group(2)).strip()
        remixer = remixer.replace("None", "") #please never do this
    return artist + remixer

def get_title(name: str) -> str:
    title_raw = re.search(r"(?: - )(.+)(?:\[)", name)
    if title_raw == None:
        title_raw = re.search(r"(?: - )(.+)(?:-[a-zA-Z0-9_\-]{11}\.\.?description)$", name)
        if title_raw == None:
            utils.notify_admins(f"Something went wrong in parsing the title! title_raw = {title_raw}s")
            return "bruhbruhburbrbh"
    title = title_raw.group(1).strip()
    return title

def get_orig_link(name: str) -> str:
    orig_link_raw = re.search(r"([a-zA-Z0-9_\-]{11})(?:\.\.?description)$", name)
    orig_link = orig_link_raw.group(1).strip()
    return "https://youtu.be/" + orig_link


def get_label(desc: str) -> str:
    #Label
    label_raw = re.search(r"(Label: )(.*)", desc)
    if label_raw == None or re.search(r"\d{7}_Records_DK"):
        return '-'
    label = label_raw.group(2).strip()
    label = re.sub(r'[\\/\(\)\[\]]', '', label)
    label = re.sub(r'[-\. ]', '_', label)
    label = re.sub(r'[\[\]\(\)]', '', label)

    # label = '#' + label.replace('\'', '').replace('/', '').replace('(', '')
    #                    .replace('-', '_').replace('.', '_').replace(' ', '_')

    return '#' + label.strip('_')

def get_catalogue(name: str) -> str:
    #Catalogue
    catalogue_raw = re.search(r"\[(.+)\]", name)

                            # removes label names from distrokid,
                            # as they are unique for each release and are useless
    if catalogue_raw == None:
        return '-'
    catalogue = catalogue_raw.group(1).strip()
    return catalogue

# def get_genre(desc):
#     #Genre, style
#     genre_raw = re.search(r"(Genre: )(.*)", desc)
#     if genre_raw == None:
#         genre_raw = 'Electronic'
#         genre = genre_raw
#         return "#" + genre
#     else:
#         genre = genre_raw.group(2).strip()
#         return "#" + genre

        # print("{}: {}".format(_dbgl(), str(style)))

def get_style(desc: str) -> str:
    style_raw = re.search(r"(Style: )(.*)", desc)

    if style_raw == None:
        return "#Electronic"
    else:
        style = style_raw.group(2).strip()
        res = ""
        style = style.replace('#', '')
        splitted = _splitter(style)
        for ch in splitted:
            out = "#" + ch.strip().replace(" ", "_")
            out = out.replace(".", "")
            res = res + out + " "
        return res.strip('_')

def get_support_links(desc: str) -> str:
    # reg = re.compile(r"(?:https?:\/\/(?:\S| )*$)(?=[\s\S]+^Artist)", re.M)
    # support_links_raw = reg.search(desc)
    support_links = re.search(r"(?:https?:\/\/(?:\S| )*$)(?=[\s\S]+^Artist)", desc)
    return support_links.group(0).strip() if support_links else ""

def _splitter(inp: str) -> str:
    if inp.find("|") != -1:
        splitted = inp.split("|")
        return splitted
    if inp.find(",") != -1:
        splitted = inp.split(",")
        return splitted
    else:
        splitted = inp.split(" ")
        return splitted

def hash_artist(artist: str) -> str:
    splitted = artist.split('&')
    res = ''
    for sp in splitted:
        if re.search(r'\D', sp):
            res = res + '#' + re.sub(r'[-\. ]', '_', sp).strip('_') + ' '
        else:
            res = res + '#The_' + re.sub(r'[-\. ]', '_', sp).strip('_') + ' '
    return res

def get_final_caption(descr_name: str, descr_contents: str, debug_toggle=0) -> str:
    """
        Get final post caption
        :param descr_name: name of description file
        :param descr_contents: description contents
        :param debug_toggle: (default = 0) debug toggle for song name
    """
    descr_name = os.path.basename(descr_name)
    upload_type = get_upload_type(descr_contents)
    if upload_type == 1:
        final = "Artist(s): "       + hash_artist(get_artist        (descr_name))      + "\n" + \
                "Label: "           +             get_label         (descr_contents)   + "\n" + \
                "Catalogue: "       +             get_catalogue     (descr_name)       + "\n" + \
                "Genre: "           +             get_style         (descr_contents)   + "\n" + \
                f"<a href='{get_support_links(descr_contents)}'>Support</a>"  + '   ' + f"<a href='{get_orig_link(descr_name)}'>Original upload</a>" + \
                debug_toggle * ("debug_Title: "+  get_title         (descr_name))

    elif upload_type == 2:
        podcast, podcast_author, soundcloud = get_podcast_info(descr_contents)
        final = podcast + " " + podcast_author + "\n" + "\n" + soundcloud + "\n" + "\n" + "Original upload: " + get_orig_link(descr_name)

    elif upload_type == 3:
        final_raw = re.search(r'[\s\S]+?(?=Follow.+here:)', descr_contents)
        final = final_raw.group(0).strip() + "\n" + "\n" + "Original upload: " + get_orig_link(descr_name)

    else:
        final = ""

    return final


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
    description = open("D:\\test\\desc\\descriptions\\" + name, "r", encoding="utf-8")

    # dir_list = os.listdir("D:\\test\\desc\\descriptions\\")
    # name = dir_list[random.randint(0, 656)]
    # description = open("D:\\test\\desc\\descriptions\\" + name, "r", encoding="utf-8")
    # print("\n" + name)


    fin_prep = description.read()
    print("\n" + get_final_caption(name, fin_prep, 1) + "\n")



if __name__ == '__main__':
    _tests()



"""
    ТУДУШКА:

    1) сделать чтобы работали эти и тестить ещё:

        Radical G - The Deserted Kingdom (Parallx Cold Eyes Mix) [RR5]-HjS6WVHiN4s.description

        Radical G - The Deserted Kingdom (10 Inch Version) [RR5]-msQyuGdUx4Y.description


"""


