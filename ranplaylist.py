import requests
import base64
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

# Replace these with your own client ID, client secret, and redirect URI
CLIENT_ID = '4e816287f3594f0d84ab810fe49a6e59'
CLIENT_SECRET = 'f26d8612f0f2401cace63b261362b560'
REDIRECT_URI = 'http://localhost:8080/'  # Updated to include port

# Define a simple HTTP server to capture the authorization code
class SpotifyAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the authorization code from the URL
        if "/?code=" in self.path:
            auth_code = self.path.split("code=")[1]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization code received! You can close this window.")
            self.server.auth_code = auth_code
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing authorization code.")

def get_authorization_code():
    scopes = 'playlist-modify-private playlist-modify-public'
    auth_url = (
        f"https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scopes.replace(' ', '%20')}"
    )
    
    # Open the authorization URL in the web browser
    webbrowser.open(auth_url)
    
    # Start a local server to listen for the redirect with the authorization code
    server = HTTPServer(('localhost', 8080), SpotifyAuthHandler)
    server.handle_request()  # Wait for a single request to capture the code
    
    return server.auth_code

def get_access_token(auth_code):
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI  # This must exactly match what you used to get the authorization code
    }
    
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    response_data = response.json()
    
    if 'access_token' in response_data:
        return response_data['access_token']
    else:
        raise Exception("Failed to retrieve access token. Response: " + response.text)

def get_user_id(token):
    url = "https://api.spotify.com/v1/me"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if response.status_code == 200:
        return response_data['id']
    else:
        raise Exception("Failed to retrieve user ID. Response: " + response.text)

def create_playlist(token, user_id, playlist_name):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "name": playlist_name,
        "description": "Playlist created via API",
        "public": False
    })
    
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()
    
    if response.status_code == 201:
        print(f"Playlist '{playlist_name}' created successfully.")
        return response_data['id']
    else:
        raise Exception("Failed to create playlist. Response: " + response.text)

def search_track(token, query):
    url = f"https://api.spotify.com/v1/search"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {
        'q': query,
        'type': 'track',
        'limit': 1
    }
    
    response = requests.get(url, headers=headers, params=params)
    response_data = response.json()
    
    if response.status_code == 200 and response_data['tracks']['items']:
        return response_data['tracks']['items'][0]['id']
    else:
        raise Exception("Failed to search for track. Response: " + response.text)

def add_tracks_to_playlist(token, playlist_id, track_ids):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "uris": [f"spotify:track:{track_id}" for track_id in track_ids]
    })
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 201:
        print("Tracks added successfully.")
    else:
        raise Exception("Failed to add tracks to playlist. Response: " + response.text)

def create_playlist_from_songs(token, user_id, playlist_name, csv_file_path):
    # Create the playlist
    playlist_id = create_playlist(token, user_id, playlist_name)
    
    # Read the CSV file and get track IDs
    track_ids = []
    with open(csv_file_path, 'r') as file:
        for line in file:
            track_name = line.strip()
            track_id = search_track(token, track_name)
            track_ids.append(track_id)
    
    # Add tracks to the playlist
    add_tracks_to_playlist(token, playlist_id, track_ids)

if __name__ == '__main__':
    auth_code = get_authorization_code()
    token = get_access_token(auth_code)
    
    # Get the authenticated user's ID
    user_id = get_user_id(token)
    
    csv_file_path = input("Enter the path to the CSV file: ")
    playlist_name = input("Enter the name of the playlist: ")
    
    try:
        create_playlist_from_songs(token, user_id, playlist_name, csv_file_path)
    except Exception as e:
        print(f"An error occurred: {e}")
