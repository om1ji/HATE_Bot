"""
Parser module for extracting data about tracks
from descriptions using regexes
"""

import re
import enum
import os
import random
from typing import List, Union

"""
    Важно! Отправлять аргумент в виде открытого и прочитанного файла
"""

# TODO: use latest regexes
RE_ALBUM_TITLE = re.compile(r"(Title: )(.*)", re.I)
RE_TYPE_PODCAST = re.compile(r'(\d+ Hate Podcast with )(.+)\n|(\d+ Hate Podcast with )(.+) \n', re.I)
RE_TYPE_REGULAR = re.compile(r'(Artists?: |Title: |Label: |Genre: )', re.I)
RE_SOUNDCLOUD = re.compile(r'Download.+:\n.+', re.I)
RE_ARTIST = re.compile(r"(.+)(?: ?- )")
RE_REMIX = re.compile(r"(?<=\()(.+)(?= Remix\))|(?<=\()(.+)(?= Edit\))")
_RE_YT_LINK = r'[a-zA-Z0-9_\-]{11}\.\.?description)$'

class UploadType(enum.Enum):
    RELEASE = "release",
    PODCAST = "podcast",
    OTHER = "other"

def multiple_or(*items):
    """Equivalent to `i1 or i2 or i3 or ... or iN`"""
    for item in items:
        if item:
            return item
    return items[-1]

def get_upload_type(name: str, desc: str) -> UploadType:
    podcast_check = all([
        re.search(r"Hate Podcast", desc, re.I),
        re.search(r"Downloads? and Tracklists?", desc, re.I),
    ])
    if podcast_check:
        return UploadType.PODCAST
    
    release_check = all([
        re.search(r"DISCLAIMER: ", desc),
        re.search(r"Artists?: ", desc, re.I),
        re.search(r" - ", name),
        re.search(r"Title: ", desc, re.I),
    ])
    if release_check:
        return UploadType.RELEASE
    
    return UploadType.OTHER

def get_podcast_info(desc: str) -> str:
    pod_info_raw = re.search(r"(.+)Follow #?HATE", desc, re.I, re.DOTALL)
    if pod_info_raw:
        return pod_info_raw.group(1).strip()

def get_artist(name: str) -> str:
    ...

def get_title(name: str) -> str:
    title_raw = \
           re.search(r"(?: - )(.+)(?:\[)", name) \
        or re.search(r"(?: - )(.+)(?:-[a-zA-Z0-9_\-]{11}\.\.?description)$", name)
    
    if not title_raw:
        import utils
        utils.notify_admins(f"Something went wrong in parsing the title! {name=}")
        return "brubrhbrhbruubhbhu"
    return title_raw.group(1).strip()

def get_orig_link(name: str) -> str:
    return "https://youtu.be/" + \
        re.search(r"(.{11})\.\.?description", name).group(1).strip()

def get_label(desc: str) -> str:
    label_raw = re.search(r"(Label: )(.+)", desc)
    if not label_raw:
        return "-"
    label = label_raw.group(2).strip()
    if re.search(r"\d{7}_Records_DK", label):
        return "-"
    
    return label

def get_catalogue(desc: str, name: str) -> Union[str, None]:
    catalogue_raw = multiple_or(
        re.search(r"(?:Catalogu?e?: )(.+)", desc),
        re.search(r"\[(.+)\]", name),
        re.search(r"(?:Cat.+: )(.+)", desc)
    )
    return catalogue_raw.group(1).strip() if catalogue_raw else None

def get_style(desc: str) -> str:
    ...

def get_support_link(desc: str) -> str:
    support_raw = re.search(r"https?:\/\/\S+", desc)
    return support_raw.group(0).strip() if support_raw else None

def get_final_caption(descr_name: str, descr_contents: str, debug_toggle=0) -> str:
    """
        Get final post caption
        :param descr_name: name of description file
        :param descr_contents: description contents
        :param debug_toggle: (default = 0) debug toggle for song name
    """
    type_ = get_upload_type(descr_name, descr_contents)
    print(f"{type_=}")
    if type_ == UploadType.RELEASE:
        caption = f"""
        {get_orig_link(descr_name)=}
        {get_label(descr_contents)=}
        {get_catalogue(descr_contents, descr_name)=}
        {get_support_link(descr_contents)=}
        {get_title(descr_name)=}
        """
        return caption
    else:
        raise NotImplementedError("Support for non-release uploads is not yet implemented")


def _tests() -> None:
    """
        тестики от артеметры, не трогать
    """
    name = "Shlømo - HATE Podcast 240-1uAaiaa6Kr8..description"
    with open("D:\\test\\desc\\descriptions\\" + name, "r", encoding="utf-8") as f:
        fin_prep = f.read()
    
    # dir_list = os.listdir("D:\\test\\desc\\descriptions\\")
    # name = dir_list[random.randint(0, 656)]
    # fin_prep = open("D:\\test\\desc\\descriptions\\" + name, "r", encoding="utf-8").read()
    # print("\n" + name)

    print(f"\n{get_final_caption(name, fin_prep, 1)}\n")



if __name__ == '__main__':
    _tests()



"""
    ТУДУШКА:

    1) сделать чтобы работали эти и тестить ещё:

        Radical G - The Deserted Kingdom (Parallx Cold Eyes Mix) [RR5]-HjS6WVHiN4s.description

        Radical G - The Deserted Kingdom (10 Inch Version) [RR5]-msQyuGdUx4Y.description


"""


