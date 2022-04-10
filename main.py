# Caleb Milo
# Chart the frequency of each word used by a given artist

from bs4 import BeautifulSoup
import wikipediaapi
import requests
import re


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

    # Reformat artist name for Genius url
    artist = artist.replace('_', '-')

    discog = artistPage[artistPage.find('Discography\nStudio albums'):].split('\n')
    del discog[:3]

    albums = {}
    for line in discog:
        # Fills albums with genius URL formatted names of each studio album found in wikipedia api call
        if line == '':
            break

        albums[(line[:line.rfind('(') - 1].strip().replace(' ', '-'))] = {}


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
            lyrics = re.sub(r'\[([A-Za-z0-9_:\-$&!@* ]+)]', '', lyrics)

            # Leaving this here for now just in case i missed anything in above regex
            if lyrics.__contains__('['):
                print('wtf')
                print(lyrics)
                exit()

            changes = 0
            toChange = []
            for i in range(1, len(lyrics) - 1):
                if lyrics[i].isupper() and lyrics[i-1] != " ":
                    toChange.append(i + changes)
                    changes += 1

            for i in toChange:
                lyrics = lyrics[:i] + ' ' + lyrics[i:]

            songs[songName] = lyrics

        albums[cAlbum]['songs'] = songs
        #print(albums[cAlbum])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    pull_data(get_artist_name())
