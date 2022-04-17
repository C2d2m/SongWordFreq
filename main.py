# Caleb Milo
# Chart the frequency of each word used by a given artist

from bs4 import BeautifulSoup
import wikipediaapi
import requests
import re
import random
import matplotlib.pyplot as plt
from matplotlib import rc


def get_random_colour():
    return "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])


def get_artist_name():
    return input("Enter the artist name: ").strip().replace(" ", '_')


def pull_data(artist):
    # TODO make way more robust
    wiki_wiki = wikipediaapi.Wikipedia('en')

    artistPage = wiki_wiki.page(artist)

    if not artistPage.exists():
        print("Sorry, this artist cannot be found")
        exit(-1)

    artistPage = artistPage.text
    print(artistPage)

    # Reformat artist name for Genius url
    artist = artist.replace('_', '-')

    if artistPage.__contains__("Discography\nStudio albums"):
        discog = artistPage[artistPage.find('Discography\nStudio albums'):].split('\n')
    elif artistPage.__contains__("Discography\nAlbums"):
        discog = artistPage[artistPage.find('Discography\nAlbums'):].split('\n')
    elif artistPage.__contains__("Discography"):
        discog = artistPage[artistPage.find('Discography'):].split('\n')
    else:
        discog = artistPage[artistPage.find('Albums'):].split('\n')

    for i in range(len(discog)):
        if discog[i].__contains__('('):
            del discog[:i]
            break

    albums = {}
    for line in discog:
        # Fills albums with genius URL formatted names of each studio album found in wikipedia api call
        if line == '':
            break
        albums[line[:line.rfind('(') - 1].strip().replace(' ', '-').replace('.', '-')] = {}

    for cAlbum in albums.keys():
        # Loop through all albums to get a list of songs

        print('\nPulling Data Album:', cAlbum)

        page = requests.get('https://genius.com/albums/' + artist + '/' + cAlbum)
        soup = BeautifulSoup(page.content, 'html.parser')

        songs = {}
        songDiv = soup.findAll('div', class_='chart_row-content')
        for cSong in songDiv:
            # Loop for all the songs of the album to get their lyrics

            temp = cSong.text.strip()
            songName = temp[:temp.rfind('\n')]

            print('Pulling Lyrics From:', songName)

            cSongPage = requests.get(cSong.a['href'])
            songSoup = BeautifulSoup(cSongPage.content, 'html.parser')

            lyricDiv = songSoup.select('div[class*="Lyrics__Container"]')

            # If there are no lyrics, go to next song, else begin parsing the string
            if len(lyricDiv) == 0:
                print('There are no lyrics available for this song')
                songs[songName] = None
                continue

            lyrics = lyricDiv[0].text

            # Disgusting parsing
            lyrics = re.sub(r'\[([A-Za-z0-9_:\-$&!?;<>^+=|{}`~@*.,/\\é()#\'" ]+)]', '', lyrics)

            # Leaving this here for now just in case i missed anything in above regex
            if lyrics.__contains__('['):
                print('wtf')
                print(lyrics)
                exit()

            changes = 0
            toChange = []
            for i in range(1, len(lyrics) - 1):
                if lyrics[i].isupper() and lyrics[i - 1] != " " and not lyrics[i - 1].isupper():
                    toChange.append(i + changes)
                    changes += 1

            for i in toChange:
                lyrics = lyrics[:i] + ' ' + lyrics[i:]

            songs[songName] = lyrics

        albums[cAlbum]['songs'] = songs
    return albums


def count_words(data):
    numWords = {}

    for album in data.keys():
        numWords[album] = {}

        for song in data[album]['songs'].keys():

            if data[album]['songs'][song] is None:
                continue

            words = data[album]['songs'][song].split(' ')

            for cWord in words:
                if cWord not in numWords[album]:
                    numWords[album][cWord] = 1
                else:
                    numWords[album][cWord] += 1

    return numWords


def chart_data(data, name):
    wordsToShow = int(input('How many of the top words would you like to see (-1 for all): '))
    wordsPerAlbum = []
    albumNames = []

    topWordsDict = {}

    for album in data.keys():
        for cWord in data[album].keys():
            if cWord not in topWordsDict:
                topWordsDict[cWord] = data[album][cWord]
            else:
                topWordsDict[cWord] += data[album][cWord]

    if wordsToShow == -1:
        wordsToShow = len(topWordsDict.items()) - 1
    topWords = sorted(topWordsDict.items(), key=lambda x: x[1], reverse=True)[:wordsToShow]

    for album in data.keys():
        albumNames.append(album)
        temp = []

        for cWord in topWords:
            if cWord[0] in data[album]:
                temp.append(data[album][cWord[0]])
            else:
                temp.append(0)
        wordsPerAlbum.append(temp)

    rc('font', weight='bold')
    barWidth = 1
    xLabel = [i[0] for i in topWords]
    r = [i for i in range(wordsToShow)]
    startHeights = [0 for i in range(wordsToShow)]

    for bar in range(len(albumNames)):
        plt.bar(r, wordsPerAlbum[bar], bottom=startHeights, color=get_random_colour(), edgecolor='white',
                width=barWidth)

        for i in range(wordsToShow):
            startHeights[i] += wordsPerAlbum[bar][i]

    plt.title(name)
    plt.xticks(r, xLabel, fontweight='bold')
    plt.xlabel('Words')
    plt.legend(albumNames, loc='upper right')

    plt.savefig('freqPNG/' + artistName + '_Figure.png')

    plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    artistName = get_artist_name()

    chart_data(count_words(pull_data(artistName)), artistName)
