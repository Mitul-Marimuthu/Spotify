import requests
import json
import base64
import threading
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
import os

# Spotify API credentials
load_dotenv('.env.local')
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

#global variable to store the authorization code
auth_code = None

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
def get_recently_played_tracks(access_token):
    url = 'https://api.spotify.com/v1/me/player/recently-played'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get recently played tracks:", response.json())
        return None
    
def save_tracks(tracks):
    with open('recently_played_tracks.json', 'w') as json_file:
        json.dump(tracks,json_file, indent=4)

def save_in_file(tracks):
    list = {}
    for item in tracks['items']:
        track = item['track']

        # list[f"{track['name']}, {", ".join(artist['name'] for artist in track['artists'])}"] =  (track['album']['name'], track['album']['images'][0], 0)
        # subset = (track['name'], ", ".join(artist['name'] for artist in track['artists']), track['album']['name'], track['album']['images'][0], 0)
        if f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}" in list:
            list[f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}"][2] += 1
        else:
            list[f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}"] =  [track['album']['name'], track['album']['images'][0], 1]

    with open('save_data.txt', 'w') as file:
        for item in list:
            file.write(f"{item}, {', '.join(str(i) for i in list[item])}")
            file.write("\n")

if __name__ == "__main__":
    auth_code = get_authorization_code()
    if auth_code:
        access_token = get_access_token(auth_code)
        if access_token:
            tracks = get_recently_played_tracks(access_token)
            if tracks:
                save_in_file(tracks)
                print(f"\n\n{len(tracks['items'])}")
                for item in tracks['items']:
                    track = item['track']
                    print(f"{track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")


# #clinet_id: 2cf26052dde241b88077957dc40f963b
# #client secret: 761e102a778348988ecebe405c13a10e

# import requests
# import json
# import base64
# import webbrowser
# from urllib.parse import urlencode

# #API Credentials
# CLIENT_ID = '2cf26052dde241b88077957dc40f963b'
# CLIENT_SECRET = '761e102a778348988ecebe405c13a10e'
# REDIRECT_URI = 'https://open.spotify.com/'

# #GEt authorization code
# def get_authorization_code():
#     auth_url = "https://accounts.spotify.com/authorize"
#     scopes = "user-read-recently-played"
#     params = {
#         'client_id': CLIENT_ID,
#         'response_type': 'code',
#         'redirect_uri': REDIRECT_URI,
#         'scope': scopes,
#     }
#     url = f"{auth_url}?{urlencode(params)}"
#     print(f"Please log in here: {url}")
#     webbrowser.open(url)
#     # Manually copy the "code" parameter from the redirected URL and paste it
#     code = input("Paste the authorization code here: ")
#     return code

# #get access token
# def get_access_token(auth_code):
#     token_url = 'https://accounts.spotify.com/api/token'
#     #auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

#     data = {
#         'grant_type': 'authorization_code',
#         'code': auth_code,
#         'redirect_uri': REDIRECT_URI,
#     }
#     headers = {
#         'Authorization': f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}",
#     }

#     response = requests.post(token_url, data=data, headers=headers)
#     if response.status_code == 200:
#         return response.json()['access_token']
#     else:
#         print("failed to get access token:", response.json())
#         return None
    
# #get recently played tracks
# def get_recently_played_tracks(access_token):
#     url = 'https://api.spotify.com/v1/me/player/recently-played'
#     headers = {
#         'Authorization': f'Bearer {access_token}'
#     }
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print("Failed to get recently played tracks:", response.json())
#         return None
    
# if __name__ == "__main__":
#     auth_code = get_authorization_code()
#     if auth_code:
#         access_token = get_access_token(auth_code)
#         if access_token:
#             tracks = get_recently_played_tracks(access_token)
#             if tracks:
#                 for item in tracks:
#                     track = item['track']
#                     print(f"{track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")