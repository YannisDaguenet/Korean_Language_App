CLIENT_ID = "10Fl_hsWCp2mSpkDpyPun0HWFxFOU6IHIQT90rSAKwvdH-iBBsndVsSqLbOod2Ol"
CLIENT_KEY = "iwaJluvxxWANbli_TUZfwVxaoLl4xsToiHHYe8CW_NJjzQJ-7jUgtpxfIyBQ_M-a7ml9cEF2CO5snCgCf4EIJg"

import requests
from bs4 import BeautifulSoup

GENIUS_TOKEN = "6-Fkazz2WVrsW6oG0OZSNsmTU8d1-86i6PRTWN8xpMliL2KROenDvqfsXVlmv9MD"
BASE_URL = "https://api.genius.com"

headers = {'Authorization': f'Bearer {GENIUS_TOKEN}'}

def search_song(query):
    search_url = f"{BASE_URL}/search"
    params = {'q': query}
    response = requests.get(search_url, headers=headers, params=params)
    data = response.json()
    hits = data['response']['hits']
    return hits

def get_song_details(song_id):
    song_url = f"{BASE_URL}/songs/{song_id}"
    response = requests.get(song_url, headers=headers)
    return response.json()

def scrape_lyrics_from_url(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, "html.parser")
    lyrics_divs = html.find_all("div", class_=lambda x: x and "Lyrics__Container" in x)
    if lyrics_divs:
        lyrics = "\n".join(div.get_text(separator="\n") for div in lyrics_divs)
    else:
        # Try old layout
        lyrics_div = html.find("div", class_="lyrics")
        lyrics = lyrics_div.get_text(separator="\n") if lyrics_div else "Lyrics not found."
    return lyrics.strip()

# === Example usage ===
korean_hits = search_song("박소은")
for hit in korean_hits:
    song = hit['result']
    print(f"{song['full_title']} ({song['id']})")

    song_details = get_song_details(song['id'])
    song_url = song_details['response']['song']['url']
    print("Song page URL:", song_url)

    # Scrape lyrics directly from page
    lyrics = scrape_lyrics_from_url(song_url)
    print("Lyrics:\n", lyrics)
    print("-" * 40)
