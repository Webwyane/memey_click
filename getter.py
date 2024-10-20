import requests
import base64
import re
import csv

# Replace these with your own client ID and client secret
CLIENT_ID = '4e816287f3594f0d84ab810fe49a6e59'
CLIENT_SECRET = 'f26d8612f0f2401cace63b261362b560'

def get_access_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'client_credentials'
    }
    
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get access token. Status code: {response.status_code}. Response: {response.text}")
    
    response_data = response.json()
    
    if 'access_token' not in response_data:
        raise Exception("Access token not found in response")
    
    return response_data['access_token']

def extract_playlist_id(playlist_url):
    # Extract the playlist ID from the URL
    playlist_id_match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url)
    if playlist_id_match:
        return playlist_id_match.group(1)
    else:
        raise ValueError("Invalid playlist URL")

def get_playlist_tracks(playlist_id, token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get playlist tracks. Status code: {response.status_code}. Response: {response.text}")
    
    return response.json()

def list_songs_and_artists(playlist_url):
    token = get_access_token()
    playlist_id = extract_playlist_id(playlist_url)
    tracks = get_playlist_tracks(playlist_id, token)
    
    song_list = []
    for item in tracks['items']:
        track = item['track']
        song_list.append([track['name'], track['artists'][0]['name']])
    
    return song_list

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Song', 'Artist'])
        writer.writerows(data)

if __name__ == '__main__':
    playlist_url = input("Enter the Spotify playlist URL: ")
    try:
        songs_and_artists = list_songs_and_artists(playlist_url)
        csv_filename = 'songs_and_artists.csv'
        save_to_csv(songs_and_artists, csv_filename)
        print(f"Songs and artists have been saved to {csv_filename}")
    except Exception as e:
        print(f"An error occurred: {e}")
