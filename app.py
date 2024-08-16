from spotipy.oauth2 import SpotifyOAuth
import spotipy

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