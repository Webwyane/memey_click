import requests
import base64
import json
import webbrowser

# Replace these with your own client ID and client secret
CLIENT_ID = '4e816287f3594f0d84ab810fe49a6e59'
CLIENT_SECRET = 'f26d8612f0f2401cace63b261362b560'
REDIRECT_URI = 'http://localhost/'  # or any other redirect URI you set in your Spotify app settings

def get_authorization_code():
    scopes = 'playlist-modify-private playlist-modify-public'
    auth_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=playlist-modify-private%20playlist-modify-public"

    
    # Open the authorization URL in the web browser
    webbrowser.open(auth_url)
    
    # Ask the user to input the authorization code
    return input("Enter the authorization code from the URL: ")

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
    
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    response_data = response.json()
    
    if 'access_token' in response_data:
        return response_data['access_token']
    else:
        raise Exception("Failed to retrieve access token. Response: " + response.text)

# Rest of the functions (create_playlist, search_track, add_tracks_to_playlist, etc.) remain the same.

if __name__ == '__main__':
    auth_code = get_authorization_code()
    token = get_access_token(auth_code)
    user_id = 'your_spotify_user_id'  # Replace with your Spotify User ID
    csv_file_path = input("Enter the path to the CSV file: ")
    playlist_name = input("Enter the name of the playlist: ")
    
    try:
        create_playlist_from_songs(token, user_id, playlist_name, csv_file_path)
    except Exception as e:
        print(f"An error occurred: {e}")
