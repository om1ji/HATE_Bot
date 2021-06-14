import re, os

def artist(desc):
    artist_raw = re.search(r"((?<=Artist: ).*)|((?<=Artists: )).*", desc)
    artist = artist_raw.group(0).strip()
    return artist

def title(desc):
    title_raw = re.search(r"(?<=Title: ).*", desc)
    title = title_raw.group(0).strip()
    return title

def label(desc):
    label_raw = re.search(r"(?<=Label: ).*", desc)
    label = label_raw.group(0).strip()
    return label

def catalogue(desc):
    catalogue_raw = re.search(r"(?<=Catalogue: ).*", desc)
    catalogue = catalogue_raw.group(0).strip()
    return catalogue

def genre(desc):
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