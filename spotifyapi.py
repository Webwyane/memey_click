import requests
import base64
import json
import webbrowser
import random
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from http.server import BaseHTTPRequestHandler, HTTPServer

# Spotify API credentials and redirect URI
CLIENT_ID = '4e816287f3594f0d84ab810fe49a6e59'
CLIENT_SECRET = 'f26d8612f0f2401cace63b261362b560'
REDIRECT_URI = 'http://localhost:8080/'  # Updated to include port

# Helper function to make a POST request
def make_post_request(url, headers, data):
    response = requests.post(url, headers=headers, data=data)
    if response.status_code not in [200, 201]:
        raise Exception(f"Request failed with status {response.status_code}: {response.text}")
    return response.json()

# Helper function to make a GET request
def make_get_request(url, headers, params=None):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Request failed with status {response.status_code}: {response.text}")
    return response.json()

# Simple HTTP server to capture the authorization code
class SpotifyAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
    print(f"Opening URL: {auth_url}")
    webbrowser.open(auth_url)
    server = HTTPServer(('localhost', 8080), SpotifyAuthHandler)
    server.handle_request()
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
        'redirect_uri': REDIRECT_URI
    }
    response_data = make_post_request('https://accounts.spotify.com/api/token', headers, data)
    return response_data.get('access_token')

def get_user_id(token):
    url = "https://api.spotify.com/v1/me"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    response_data = make_get_request(url, headers)
    return response_data.get('id')

def create_playlist(token, user_id, playlist_name):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = json.dumps({"name": playlist_name, "description": "Playlist created via API", "public": False})
    response_data = make_post_request(url, headers, data)
    return response_data.get('id')

def search_track(token, query):
    url = "https://api.spotify.com/v1/search"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    params = {'q': query, 'type': 'track', 'limit': 1}
    response_data = make_get_request(url, headers, params)
    items = response_data.get('tracks', {}).get('items', [])
    return items[0]['id'] if items else None

def add_tracks_to_playlist(token, playlist_id, track_ids):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = json.dumps({"uris": [f"spotify:track:{track_id}" for track_id in track_ids]})
    make_post_request(url, headers, data)

def upload_playlist_image(token, playlist_id, image_path):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/images"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'image/jpeg'}
    with open(image_path, 'rb') as image_file:
        response = requests.put(url, headers=headers, data=image_file)
    if response.status_code != 200:
        raise Exception(f"Failed to upload image. Response: {response.text}")

def get_recommendations(token, seed_artists=None, num_recommendations=10):
    url = "https://api.spotify.com/v1/recommendations"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    params = {
        'seed_artists': ','.join(seed_artists) if seed_artists else None,
        'limit': num_recommendations
    }
    response_data = make_get_request(url, headers, params)
    return response_data.get('tracks', [])

def get_playlist_artists(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    response_data = make_get_request(url, headers)
    artists = set()
    for item in response_data.get('items', []):
        track = item.get('track')
        if track:
            artists.update(artist['id'] for artist in track.get('artists', []))
    return list(artists)

def get_random_number_of_songs(max_songs):
    return random.randint(1, max_songs)

def create_playlist_from_songs_and_recommendations(token, user_id, playlist_name, csv_file_path, image_path=None, num_of_rec=0):
    # Create the playlist
    playlist_id = create_playlist(token, user_id, playlist_name)
    
    # Upload playlist image if provided
    if image_path:
        upload_playlist_image(token, playlist_id, image_path)
    
    # Read the CSV file and get track IDs
    track_ids = []
    with open(csv_file_path, 'r') as file:
        lines = file.readlines()
    
    # Skip the first line (header) and determine the number of songs to include
    lines = lines[1:]
    num_songs = get_random_number_of_songs(len(lines))
    
    # Select a random sample of track names
    random_lines = random.sample(lines, num_songs)
    
    for line in random_lines:
        track_name = line.strip()
        track_id = search_track(token, track_name)
        if track_id:
            track_ids.append(track_id)
        else:
            print(f"Track not found: {track_name}")
    
    # Add tracks to the playlist
    add_tracks_to_playlist(token, playlist_id, track_ids)
    
    # Get artists from the playlist
    artists = get_playlist_artists(token, playlist_id)
    
    # Get recommendations based on artists
    recommended_tracks = get_recommendations(token, seed_artists=artists, num_recommendations=num_of_rec)
    
    # Extract track IDs from recommendations
    rec_track_ids = [track['id'] for track in recommended_tracks]
    
    # Add recommended tracks to the playlist
    add_tracks_to_playlist(token, playlist_id, rec_track_ids)
    
    # Return the number of songs added and recommended
    return num_songs, num_of_rec

def select_file_and_create_playlist():
    # Create the GUI
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Ask for file path
    csv_file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    
    if not csv_file_path:
        messagebox.showerror("Error", "No file selected.")
        return
    
    # Get playlist name and number of recommendations
    playlist_name = simpledialog.askstring("Input", "Enter the name of the playlist:")
    if not playlist_name:
        messagebox.showerror("Error", "No playlist name provided.")
        return
    
    num_of_rec = simpledialog.askinteger("Input", "Enter the number of recommended songs:", minvalue=1)
    if num_of_rec is None:
        messagebox.showerror("Error", "Invalid number of recommended songs.")
        return
    
    image_path = filedialog.askopenfilename(
        title="Select Playlist Image (optional)",
        filetypes=[("Image Files", "*.jpg;*.jpeg")]
    )
    
    if image_path == '':
        image_path = None
    
    # Execute the main function
    try:
        auth_code = get_authorization_code()
        token = get_access_token(auth_code)
        user_id = get_user_id(token)
        num_songs, num_rec = create_playlist_from_songs_and_recommendations(
            token, user_id, playlist_name, csv_file_path, image_path, num_of_rec
        )
        messagebox.showinfo("Success", f"Playlist created with {num_songs} songs and {num_rec} recommendations.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    select_file_and_create_playlist()
