import requests
import json
import base64
import threading
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
import os
import ast
import datetime

# Spotify API credentials
load_dotenv('.env.local')
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

#global variable to store the authorization code
auth_code = None
#globabl variable to store the list of songs
data = {}
artist_list = {}
album_list = {}
last_played = {}

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
    print(f"Please log in here: {url}")

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
    if len(last_played) > 0:
        get_recently_played_tracks_special(access_token=access_token)
    else:
        url = 'https://api.spotify.com/v1/me/player/recently-played'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            "limit": 50
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            save_new_data(response.json())
        else:
            print("Failed to get recently played tracks:", response.json())
            return None
    
def get_recently_played_tracks_special(access_token):
    url = 'https://api.spotify.com/v1/me/player/recently-played'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    after_timestamp = None
    done = False
    while not done:
        params = {
            "limit": 3
        }
        if after_timestamp:
            params["after"] = after_timestamp
        
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"ERROR: {response.status_code}, {response.json()}")
            break

        data = response.json()
        items = data.get("items", [])
        if not items: 
            break
        save_new_data(response.json(), done=done)
        after_timestamp = items[-1]['played_at']
        after_timestamp = int(
            datetime.datetime.strptime(after_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp() * 1000
        )

def save_tracks(tracks):
    with open('recently_played_tracks.json', 'w') as json_file:
        json.dump(tracks,json_file, indent=4)

#reads the current data from the file and loads it into the list dict
def read_from_file():
    global data
    global album_list
    global artist_list
    global last_played
    #file with song information and times played
    with open('frequency_list.txt', 'r') as file:
        line = file.readline()
        while line:
            params = line.split('+')
            data[params[0].strip()] = [params[1].strip(), int(params[2].strip()), []]
            line = file.readline()

    #file with the times of when the song was played
    with open('time_list.txt', 'r') as file:
        line = file.readline()
        while line:
            if '+' not in line: 
                line = file.readline()
                continue
            params = line.split('+')
            if params[0].strip() == 'first':
                last_played = {}
                last_played[params[1].strip()] = params[2].strip()
            else:
                data[params[0].strip()][2] = ast.literal_eval(params[1].strip())
            # print(data[params[0].strip()][2])
            line = file.readline()

    #file with the artists and total number of songs (iterations included) listened to by the artist
    with open('artist_list.txt', 'r') as file:
        line = file.readline()
        while line:
            params = line.split('+')
            artist_list[params[0].strip()] = int(params[1].strip())
            line = file.readline()

    #file with the albums and how many songs (iterations included) listened to in the album
    with open('album_list.txt', 'r') as file:
        line = file.readline()
        while line:
            params = line.split('+')
            album_list[params[0].strip()] = [params[1].strip(), int(params[2].strip())]
            line = file.readline()


    # print('IN LIST: ')
    # for key in list:
    #     print(f"{key} + {list[key]}")


#saves the relevant data into the new file
#TODO: include list of all the 'played_ats'
# check if 'played_at' is in the list
# makes note of the most recently played song and its timestamp for later data collection
def save_new_data(tracks, done=False):
    global data
    global album_list
    global artist_list
    global last_played
    print(len(last_played))
    if len(last_played) == 0:
        last_played[tracks['items'][0]['track']['name']] = tracks['items'][0]['played_at']
    for item in tracks['items']:
        track = item['track']

        # list[f"{track['name']}, {", ".join(artist['name'] for artist in track['artists'])}"] =  (track['album']['name'], track['album']['images'][0], 0)
        # subset = (track['name'], ", ".join(artist['name'] for artist in track['artists']), track['album']['name'], track['album']['images'][0], 0)

        #if the "song - artist" key exists in the lsit, update its listen counter
        #otherwise add the new song into the list
        key = f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}"
        if key in data:
            #print(list[key])
            if not item['played_at'] in data[key][2]:
                data[key][1] += 1
                data[key][2].append(item['played_at'])
                update_artist_counter(track)
                update_album_counter(track)
            else:
                done = True
                break
        else:
            data[key] =  [f"{track['album']['name']} , {track['album']['images'][0]}", 1, [item['played_at']]]
            update_artist_counter(track)
            update_album_counter(track)


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

#sorts all of the dictionaries accordingly
def sorts():
    global data
    global album_list
    global artist_list
    data = dict(sorted(data.items(), key=lambda item: item[1][1], reverse=True))
    album_list = dict(sorted(album_list.items(), key=lambda item: item[1][1], reverse=True))
    artist_list = dict(sorted(artist_list.items(), key=lambda item: item[1], reverse=True))

# writes the content of the list into the file in a way that makes it easy to extract
#TODO: include the 'played_at list after'
def write_to_file():
    global data
    global artist_list
    global album_list
    global last_played
    with open('frequency_list.txt', 'w') as file:
        for item in data:
            #adds a + sign to discern between the three components of the input
            # 1. "(song name) - (artist)"
            # 2. "(album name), {image information}"
            # 3. frequency counter
            file.write(f"{item} + {data[item][0]} + {data[item][1]}")
            file.write("\n")
    
    # writes to the file that stores the times that all the songs were played
    with open('time_list.txt', 'w') as file:
        if len(last_played) > 0:
            for item in last_played:
                file.write(f"first + {item} + {last_played[item]}\n\n")
        for item in data:
            file.write(f"{item} + {data[item][2]}\n")

    # writes to the file that stores the number of albums listened to and the number of songs
    # listened to from the album
    #print(album_list)
    with open('album_list.txt', 'w') as file:
        for item in album_list:
            file.write(f"{item} + {album_list[item][0]} + {album_list[item][1]}\n")

    #writes to the file that stores the number of songs listened to by an artist
    #print('a')
    #print(artist_list)
    with open('artist_list.txt', 'w') as file:
        for item in artist_list:
            file.write(f"{item} + {artist_list[item]}\n") 

if __name__ == "__main__":
    read_from_file()
    auth_code = get_authorization_code()
    if auth_code:
        access_token = get_access_token(auth_code)
        if access_token:
            get_recently_played_tracks_normal(access_token)
            # if tracks:
            #     save_new_data(tracks)
            sorts()
            write_to_file()
                
    #             print(f"\n\n{len(tracks['items'])}")
                # for item in tracks['items']:
                #     track = item['track']
                #     print(f"{track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")
