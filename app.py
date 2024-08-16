from spotipy.oauth2 import SpotifyOAuth
import spotipy

def create_spotify_client():
    global sp
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                       client_secret=client_secret,
                                                       redirect_uri=redirect_uri,
                                                       scope=scope))
    except Exception as e:
        print(e)