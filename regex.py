import re, os

"""
    Важно! Отправлять аргумент в виде открытого и прочитанного файла

"""

def artist(desc):
    #Artist
    artist_raw = re.search(r"(?<=Artist: ).*", desc)
    artist = artist_raw.group(0).strip()
    return artist

def title(desc):
    #Title
    title_raw = re.search(r"(?<=Title: ).*", desc)
    title = title_raw.group(0).strip()
    return title

def label(desc):
    #Label
    label_raw = re.search(r"(?<=Label: ).*", desc)
    label = label_raw.group(0).strip()
    return label

def catalogue(desc):
    #Catalogue
    catalogue_raw = re.search(r"(?<=Catalogue: ).*", desc)
    catalogue = catalogue_raw.group(0).strip()
    return catalogue

def genre(desc):
    #Genre, style
    genre_raw = re.search(r"(?<=Genre: ).*", desc)
    if genre_raw == None:
        genre_raw = 'Electronic'
        genre = genre_raw
        return genre
    else:
        genre = genre_raw.group(0).strip()
        return genre

def style(desc):
    style_raw = re.search(r"(?<=Style: ).*", desc)

    if style_raw == None:
        style_raw = ""
        style = style_raw
        return style
    else:
        style = style_raw.group(0).strip()
        return style

def to_hashtag(inp):
    if inp == "":
        return ""
    inp = re.sub(r'#', '', inp)  
    inp = re.sub(r' ', '_', inp)  
    
    out = "#" + inp
    return out

# Кроме этого файла
def final(descr):
    final = "Artists: " +  to_hashtag(artist(descr)) + "\n" + "Label: " +  to_hashtag(label(descr)) + "\n" + "Catalogue: " +  catalogue(descr) + "\n" + "Genre: " +  to_hashtag(genre(descr)) + " , "  + to_hashtag(style(descr))
    return final

def metadata(description):
    output_set = []
    output_set.append(artist(description))
    output_set.append(title(description))
    output_set.append(catalogue(description))
    return output_set 