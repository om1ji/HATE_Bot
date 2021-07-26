import re, os
import random
import inspect

"""
    Важно! Отправлять аргумент в виде открытого и прочитанного файла

"""

#Берёт автора с самого релиза/альбома. Скорее всего уберу:

#def artist(desc):
#    #Artist
#    artist_raw = re.search(r"(Artists?: )(.*)", desc)
#    artist = artist_raw.group(2).strip()
#    return artist

#Берёт название с самого релиза/альбома, для метаданных

def get_album_title(desc):
   #Title
   title_raw = re.search(r"(Title: )(.*)", desc)
   title = title_raw.group(2).strip()
   return title

"""
    ОЧЕНЬ ВАЖНО!! В аргумент функций artist, title и orig_link подаётся НАЗВАНИЕ описания, а не его содержимое
"""

def get_upload_type(desc):
    """
    Returns the upload type of the video:
    1- regular release
    2 - podcast
    3 - special/other/unmathed
    """
    _type_raw = re.search(r'(\d+ Hate Podcast with )(.+)\n|(\d+ Hate Podcast with )(.+) \n', desc)
    if _type_raw != None:
        return 2
    else:
        _type_raw = re.search(r'(Artists?: |Title: |Label: |Genre: )', desc)
        if _type_raw != None:
            return 1
        else:
            return 3 
        

def get_podcast_info(desc):
    _podcast_descr_raw = re.search(r'(\d+ Hate Podcast with )(.+)\n|(\d+ Hate Podcast with )(.+) \n', desc)
    _podcast_descr = _podcast_descr_raw.group(1).strip()
    _podcast_author = _podcast_descr_raw.group(2).strip()
    _soundcloud = re.search(r'Download.+:\n.+', desc).group(0).strip()

    _podcast_author = re.sub(r'[\[\]\(\)\.]', '', _podcast_author)
    _podcast_author = _podcast_author.replace(' ', '_')
    _podcast_author = '#' + _podcast_author
    
    return _podcast_descr, _podcast_author, _soundcloud

def get_artist(name):
    #Artist
    artist_raw = re.search(r"(.+)(?: ?- )", name)
    if artist_raw == None:
        return "Unknown"
    artist = artist_raw.group(1).strip()
    remixer_raw = re.search('(?<=\()(.+)(?= Remix\))|(?<=\()(.+)(?= Edit\))', name, re.IGNORECASE)
    if remixer_raw == None:
        remixer = ""
    else:
        remixer = " & " + str(remixer_raw.group(1)).strip() + str(remixer_raw.group(2)).strip()
        remixer = remixer.replace("None", "") #please never do this
    return artist + remixer

def get_title(name):
    title_raw = re.search(r"(?: - )(.+)(?:\[)", name)
    if title_raw == None:
        title_raw = re.search(r"(?: - )(.+)(?:-[a-zA-Z0-9_\-]{11}\.\.?description)$", name)
        if title_raw == None:
            return "bruhbruhburbrbh"
    title = title_raw.group(1).strip()
    return title

def get_orig_link(name):
    orig_link_raw = re.search(r"([a-zA-Z0-9_\-]{11})(?:\.\.?description)$", name)
    orig_link = orig_link_raw.group(1).strip()
    return "https://youtu.be/" + orig_link
    

def get_label(desc):
    #Label
    label_raw = re.search(r"(Label: )(.*)", desc)
    if label_raw == None:
        return '-'
    label = label_raw.group(2).strip()
    label = re.sub(r'[\\/\(\)\[\]]', '', label)
    label = re.sub(r'[-\. ]', '_', label)
    label = re.sub(r'[\[\]\(\)]', '', label)

    # label = '#' + label.replace('\'', '').replace('/', '').replace('(', '')
    #                    .replace('-', '_').replace('.', '_').replace(' ', '_')
    
    return '#' + label.strip('_')

def get_catalogue(name):
    #Catalogue
    catalogue_raw = re.search(r"\[(.+)\]", name)
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

def get_style(desc):
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

def get_support_links(desc):
    reg = re.compile(r"(?:https?:\/\/(?:\S| )*$)(?=[\s\S]+^Artist)", re.M)
    support_links_raw = reg.search(desc)
    
    if support_links_raw == None:
        return ""
    else:
        support_links = support_links_raw.group(0).strip()
        return support_links


def _splitter(inp):
    if inp.find("|") != -1:
        splitted = inp.split("|")
        return splitted
    if inp.find(",") != -1:
        splitted = inp.split(",")
        return splitted
    else:
        splitted = inp.split(" ")
        return splitted

def hash_artist(artist):
    splitted = artist.split('&')
    res = ''
    for sp in splitted:
        if re.search(r'\D', sp):
            res = res + '#' + re.sub(r'[-\. ]', '_', sp).strip('_') + ' '
        else:
            res = res + '#The_' + re.sub(r'[-\. ]', '_', sp).strip('_') + ' '
            
    return res



def get_final_caption(descr_name, descr_contents, debug_toggle=0):
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


def get_metadata(description):
    output_set = []
    output_set.append(get_artist(description))
    output_set.append(get_title(description))
    output_set.append(get_catalogue(description))
    return output_set 



def _tests():
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


