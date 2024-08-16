from flask import Flask, request, jsonify
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from spotipy.exceptions import SpotifyException
from requests.exceptions import HTTPError

app = Flask(__name__)

# App's credentials
client_id = '7006daa4e47f43cda68705c1df95bf1a'
client_secret = 'de4f3027c8724bf3b29e98c28230514c'
redirect_uri = 'http://localhost:8888/callback' 

scope = 'user-library-read playlist-read-private'

# Global sporipy instance
sp = None

def create_spotify_client():
    global sp
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                       client_secret=client_secret,
                                                       redirect_uri=redirect_uri,
                                                       scope=scope))
    except Exception as e:
        print(e)
        
@app.route('/connect', methods=['GET'])
def connect_spotify():
    try:
        create_spotify_client()
        if sp is not None:
            return jsonify({"message": "Spotify client connected."}), 200
        else:
            return jsonify({"error": "Failed to connect to Spotify."}), 500
    except Exception as e:
        app.logger.error(f"Error in /connect endpoint: {str(e)}")
        return jsonify({"error": "An unexpected error occurred while connecting to Spotify."}), 500
    

@app.route('/disconnect', methods=['GET'])
def disconnect_spotify():
    try:
        global sp
        sp = None
        return jsonify({"message": "Spotify client disconnected."}), 200
    except Exception as e:
        app.logger.error(f"Error in /disconnect endpoint: {str(e)}")
        return jsonify({"error": "An unexpected error occurred while disconnecting from Spotify."}), 500
    

def get_liked_songs(sp, limit=50):
    try:
        liked_songs = []
        results = sp.current_user_saved_tracks(limit=limit)
        for item in results['items']:
            track = item['track']
            liked_songs.append(track['id'])
        return liked_songs
    except SpotifyException as se:
        app.logger.error(f"Spotify API error in get_liked_songs: {str(se)}")
        raise
    except Exception as e:
        app.logger.error(f"Error getting liked songs: {str(e)}")
        raise