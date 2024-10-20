import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import base64
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

# Replace these with your own client ID, client secret, and redirect URI
CLIENT_ID = '4e816287f3594f0d84ab810fe49a6e59'
CLIENT_SECRET = 'f26d8612f0f2401cace63b261362b560'
REDIRECT_URI = 'http://localhost:8080/'

# Global variables
top_tracks = []
track_checkboxes = []
track_frame = None  # Initialize track_frame globally
scrollbar = None  # Initialize scrollbar globally

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
    scopes = 'playlist-modify-private playlist-modify-public user-top-read'
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

def display_tracks(tracks):
    global track_checkboxes, track_frame, scrollbar

    # Clear any existing checkboxes
    if track_frame:
        for widget in track_frame.winfo_children():
            widget.destroy()

    track_checkboxes = []

    # Create a checkbox for each track
    for track in tracks:
        var = tk.BooleanVar(master=track_frame)  # Pass track_frame as master
        track_checkboxes.append((track, var))  # Store track dict and variable
        checkbox = tk.Checkbutton(track_frame, text=track['name'], variable=var)
        checkbox.pack(anchor='w')

def fetch_and_display_tracks(token):
    global top_tracks
    top_tracks_data = requests.get("https://api.spotify.com/v1/me/top/tracks", headers={'Authorization': f'Bearer {token}'}).json()
    top_tracks = top_tracks_data['items']

    display_tracks(top_tracks)

# Function to authenticate and fetch the top tracks
def authenticate_spotify():
    auth_code = get_authorization_code()
    token = get_access_token(auth_code)

    # Get the authenticated user's ID
    user_id = get_user_id(token)

    # Initialize the GUI after authentication
    init_gui(token, user_id)

    # Fetch user's top tracks after GUI initialization
    fetch_and_display_tracks(token)

def init_gui(token, user_id):
    global genre_combobox, track_frame, track_checkboxes, result_label, playlist_name_entry, song_limit_entry, scrollbar

    # Create the Tkinter window
    root = tk.Tk()
    root.title("Spotify Playlist Creator with Genre Filter")

    # Entry to input playlist name
    playlist_name_label = tk.Label(root, text="Enter Playlist Name:")
    playlist_name_label.pack(pady=5)

    playlist_name_entry = tk.Entry(root, width=30)
    playlist_name_entry.pack(pady=5)

    # Entry to specify number of songs
    song_limit_label = tk.Label(root, text="Enter Number of Songs in Playlist:")
    song_limit_label.pack(pady=5)

    song_limit_entry = tk.Entry(root, width=10)
    song_limit_entry.pack(pady=5)
    song_limit_entry.insert(0, '10')  # Default limit is 10 songs

    # Genre drop-down label
    genre_label = tk.Label(root, text="Select Genre:")
    genre_label.pack(pady=5)

    # Genre drop-down (ComboBox)
    genre_combobox = ttk.Combobox(root, state="readonly", values=[
        'All', 'Pop', 'Rock', 'Hip-Hop', 'R&B', 'Classical', 'Jazz', 'Electronic', 'Reggae'
    ])
    genre_combobox.set('All')  # Set default value
    genre_combobox.pack(pady=5)

    # Button to create the playlist
    create_playlist_button = tk.Button(root, text="Create Playlist", command=lambda: create_playlist_and_add_tracks(token, user_id))
    create_playlist_button.pack(pady=10)

    # Frame for track checkboxes with scrollbar
    track_frame = tk.Frame(root)
    track_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(track_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    track_canvas = tk.Canvas(track_frame, yscrollcommand=scrollbar.set)
    track_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=track_canvas.yview)

    # Initialize frame for checkboxes
    track_frame = tk.Frame(track_canvas)
    track_canvas.create_window((0, 0), window=track_frame, anchor='nw')

    # Update the scrollbar region
    track_frame.bind("<Configure>", lambda e: track_canvas.config(scrollregion=track_canvas.bbox("all")))

    result_label = tk.Label(root, text="")
    result_label.pack(pady=5)

    root.mainloop()  # Start the Tkinter event loop

def create_playlist_and_add_tracks(token, user_id):
    playlist_name = playlist_name_entry.get()
    song_limit = int(song_limit_entry.get())
    selected_genre = genre_combobox.get()

    # Create the playlist
    playlist_id = create_playlist(token, user_id, playlist_name)

    # Get selected track IDs
    track_ids = []
    for track, var in track_checkboxes:
        if var.get():  # If checkbox is checked
            track_ids.append(track['id'])  # Use the Spotify track ID

    # Limit the number of tracks added
    track_ids = track_ids[:song_limit]

    # Add tracks to the playlist
    if track_ids:
        add_tracks_to_playlist(token, playlist_id, track_ids)
        result_label.config(text=f"Added {len(track_ids)} tracks to '{playlist_name}'.")
    else:
        result_label.config(text="No tracks selected.")

if __name__ == "__main__":
    authenticate_spotify()
