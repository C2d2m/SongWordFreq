# Caleb Milo
# Chart the frequency of each word used by a given artist

from bs4 import BeautifulSoup
import wikipediaapi
import requests


def get_artist_name():
    return input("Enter the artist name").replace(" ", '_')


def pull_data(artist):
    wiki_wiki = wikipediaapi.Wikipedia('en')

    artistPage = wiki_wiki.page(artist).text

    # Reformat artist name for Genius url
    artist = artist.replace('_', '-')

    discog = artistPage[artistPage.find('Discography'):].split('\n')
    discog.remove('Discography')

    albums = {}

    for line in discog:
        # Fills albums with genius URL formatted names of each studio album found in wikipedia api call
        if line == '':
            break
        if line.__contains__('Studio albums'):
            line = line.replace('Studio albums', '')

        albums[(line[:line.rfind('(') - 1].strip().replace(' ', '-'))] = {}

    for cAlbum in albums.keys():
        # Loop through all albums to get a list of songs

        print('\nPulling Data Album:', cAlbum)

        page = requests.get('https://genius.com/albums/' + artist + '/' + cAlbum)
        soup = BeautifulSoup(page.content, 'html.parser')

        songs = {}
        songDiv = soup.findAll('div', class_='chart_row-content')
        for cSong in songDiv:
            temp = cSong.text.strip()
            songName = temp[:temp.rfind('\n')]

            print('Pulling Lyrics From:', songName)

            cSongPage = requests.get(cSong.a['href'])
            songSoup = BeautifulSoup(cSongPage.content, 'html.parser')

            lyricDiv = songSoup.select('div[class*="Lyrics__Container"]')

            if len(lyricDiv) == 0:
                print('There are no lyrics available for this song')
                continue

            print(lyricDiv[0].text)

            lyrics = ''
            songs[songName] = lyrics

        #albums[cAlbum]['songs'] = songs
        #print(albums[cAlbum])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pull_data('Yung_Lean')
