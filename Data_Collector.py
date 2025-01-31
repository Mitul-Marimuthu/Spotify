import requests
import json
import base64
import threading
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
import os
import datetime
import pandas as pd
import sqlite3
#import ast
from File_Handlers import File_Handlers


# Spotify API credentials
load_dotenv('/Users/mitul/Desktop/spotify/.env.local')
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

#global variable to store the authorization code
auth_code = None
#globabl variable to store the list of songs
#main_list
# data = {}
# artist_list = {}
# album_list = {}
# last_played = {}
# num_songs = [0]

#global dbs
conn = sqlite3.connect("/Users/mitul/Desktop/spotify/data_files/spotify.db")
# main_list = pd.read_sql("SELECT * FROM main", conn)
# artists = pd.read_sql("SELECT * FROM artists", conn)
# album = pd.read_sql("SELECT * FROM albums", conn)
# times = pd.read_sql("SELECT * FROM times", conn)
last = pd.read_sql("SELECT * FROM last", conn)
conn.close()


start_date = '2025-01-25'

#HTTP server to hadnle the redirect and capture the auth code
class AuthorizationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = self.path.split('?')[1] if '?' in self.path else ''
        params = dict(pair.split('=') for pair in query.split('&') if '=' in pair)
        if 'code' in params:
            auth_code = params['code']
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Authorization Successful</title></head>
                <body>
                    <h1>Authorization successful!</h1>
                    <p>You can close this window.</p>
                    <script>window.close();</script>
                </body>
                </html>
            """)
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Authorization Failed</title></head>
                <body>
                    <h1>Authorization failed.</h1>
                    <p>Please try again.</p>
                </body>
                </html>
            """)


def start_http_server():
    server = HTTPServer(('localhost', 8888), AuthorizationHandler)
    server.handle_request()

# Step 1: Get Authorization Code (automated)
def get_authorization_code():
    global auth_code
    auth_url = "https://accounts.spotify.com/authorize"
    scopes = "user-read-recently-played"
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': scopes,
    }
    url = f"{auth_url}?{urlencode(params)}"
    #print(f"Please log in here: {url}")

    #start the loal server in a separate thread
    threading.Thread(target=start_http_server, daemon=True).start()

    # open the authorization URL in the default browser
    import webbrowser
    webbrowser.open(url)
    
    # wait until the auth_code is set by the server
    while auth_code is None:
        pass


    return auth_code

# Step 2: Exchange Authorization Code for Access Token
def get_access_token(auth_code):
    token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
    }
    headers = {
        'Authorization': f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}"
    }
    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print("Failed to get access token:", response.json())
        return None

# Step 3: Get Recently Played Tracks
# fetches all the tracks up until the last recently played track
def get_recently_played_tracks_normal(access_token):
    global last_played
    # print(len(last_played))
    # if len(last_played) > 0:
    #     get_recently_played_tracks_special(access_token=access_token)
    url = 'https://api.spotify.com/v1/me/player/recently-played'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        "limit": 50
    }
    response = requests.get(url, headers=headers, params=params)
    tracks = response.json()
    if response.status_code == 200:
        save_new_data(tracks)
    else:
        print("Failed to get recently played tracks:", response.json())
        return None
    #last_played.clear()
    #last_played[tracks['items'][0]['track']['name']] = tracks['items'][0]['played_at']

def save_tracks(tracks):
    with open('/Users/mitul/Desktop/spotify/test_files/recently_played_tracks.json', 'w') as json_file:
        json.dump(tracks,json_file, indent=4)

#saves the relevant data into the new file
#TODO: include list of all the 'played_ats'
# check if 'played_at' is in the list
# makes note of the most recently played song and its timestamp for later data collection
def save_new_data(tracks):
    last_p = [tracks['items'][0]['track']['name'], tracks['items'][0]['played_at']]
    l = pd.DataFrame(last_p)
    conn = sqlite3.connect("/Users/mitul/Desktop/spotify/data_files/spotify.db")
    l.to_sql("last", conn, index=True, if_exists="replace")
    cursor = conn.cursor()
    for item in tracks['items']:
        track = item['track']
        artist = ", ".join(art['name'] for art in track['artists'])
        name = track['name']
        cursor.execute('SELECT EXISTS(SELECT 1 FROM main WHERE "Song Name" = ? and "Artists" = ?)', (name, artist))
        exists = cursor.fetchone()[0]
        if exists:
            temp = cursor.execute('SELECT "Listen History" FROM times WHERE "Song" = ? AND "Artist" =? ', (name, artist))
            result = cursor.fetchone()
            times = json.loads(result[1]) 
            if item['played_at'] in times:
                break
            else:
                #FREQUENCY UPDATE
                times.append(item['played_at'])
                temp = cursor.execute('SELECT "Times Played" FROM main WHERE "Song" = ? AND "Artist" = ?', (name, artist))
                num_played = cursor.fetchone()
                cursor.execute('UPDATE main SET "Times Played" = ? WHERE "Song Name" = ? AND "Artist" = ?', (num_played[4]+1, name, artist))
                #num_art = []
                #ARTIST UPDATE
                art = artist.split(",")
                for a in art:
                    temp = cursor.execute('SELECT "Songs Listened To" FROM artists WHERE "Artist" = ?', a)
                    num_a = cursor.fetchone()
                    #n_a = num_a(1)
                    cursor.execute('UPDATE artists SET "Songs Listened To" = ? WHERE "Artist" = ?', (num_a[1]+1, a))
                
                #temp = cursor.execute("SELECT Songs Listened To FROM artists WHERE Artist = ?")
                #num_art = 1
                #ALBUM UPDATE
                alb = track['album']['name']
                alb_art = ", ".join(a['name'] for a in track['album']['artists'])
                temp = cursor.execute('SELECT "Number of Songs" FROM albums WHERE "Album" = ? AND "Artist" = ?', (alb, alb_art))
                num_alb = cursor.fetchone()
                cursor.execute('UPDATE albums SET "Number of Songs" = ? WHERE "Album" = ? AND "Artist" = ?', (num_alb[2]+1, alb, alb_art))

                #TIMES UPDATE
                cursor.execute('UPDATE times SET "Listen History" = ? WHERE "Song" = ? AND "Artist" = ?', (json.dumps(times), name, artist))

                conn.commit()
    conn.close()


    
    # global data
    # global last_played
    # #print(len(last_played))
    # if len(last_played) == 0:
    #     last_played[tracks['items'][0]['track']['name']] = tracks['items'][0]['played_at']
    # for item in tracks['items']:
    #     track = item['track']
    #     #print(track)    
    #     # list[f"{track['name']}, {", ".join(artist['name'] for artist in track['artists'])}"] =  (track['album']['name'], track['album']['images'][0], 0)
    #     # subset = (track['name'], ", ".join(artist['name'] for artist in track['artists']), track['album']['name'], track['album']['images'][0], 0)

    #     #if the "song - artist" key exists in the lsit, update its listen counter
    #     #otherwise add the new song into the list
    #     key = f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}"
    #     if key in data:
    #         #print(list[key])
    #         if item['played_at'] == list(last_played.items())[0][1]:
    #             #done = True
    #             break
    #         else:
    #             data[key][1] += 1
    #             data[key][2].append(item['played_at'])
    #             update_artist_counter(track)
    #             update_album_counter(track)
    #         # else:
    #         #     done = True
    #         #     break
    #     else:
    #         data[key] =  [f"{track['album']['name']} , {track['album']['images'][0]}", 1, [item['played_at']]]
    #         update_artist_counter(track)
    #         update_album_counter(track)
    # #print('c')


#updates the artist counter
def update_artist_counter(track):
    global artist_list
    for artist in track['artists']:
        name = artist['name']
        if name in artist_list:
            artist_list[name] += 1
        else:
            artist_list[name] = 1

#updates the album counter
def update_album_counter(track):
    global album_list
    name = track['album']['name']
    artists = ", ".join(artist['name'] for artist in track['album']['artists'])
    if track['album']['name'] in album_list:
        album_list[name][1] += 1
    else:
        album_list[name] = [artists, 1]

#all from beta (txt) version
#sorts all of the dictionaries accordingly
# def sorts():
#     global data
#     global album_list
#     global artist_list
#     data = dict(sorted(data.items(), key=lambda item: item[1][1], reverse=True))
#     album_list = dict(sorted(album_list.items(), key=lambda item: item[1][1], reverse=True))
#     artist_list = dict(sorted(artist_list.items(), key=lambda item: item[1], reverse=True))

# def read_from_files():
#     global data
#     global artist_list
#     global album_list
#     global last_played
#     global num_songs
#     File_Handlers.read_from_file(data, album_list, artist_list, last_played, num_songs, start_date)
    #print(num_songs)

    #print(c_last_played)

# def write_to_files():
#     global data
#     global artist_list
#     global album_list
#     global last_played
#     File_Handlers.write_to_file(data, album_list, artist_list, last_played)

def check():
    pass

def collect_data():
    #read_from_files()
    auth_code = get_authorization_code()
    if auth_code:
        access_token = get_access_token(auth_code)
        if access_token:
            get_recently_played_tracks_normal(access_token)
            # if tracks:
            #     save_new_data(tracks)
            #sorts()
            #write_to_files()

if __name__ == "__main__":
    collect_data()
                
    #             print(f"\n\n{len(tracks['items'])}")
                # for item in tracks['items']:
                #     track = item['track']
                #     print(f"{track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")
