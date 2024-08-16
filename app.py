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
    
@app.route('/search_playlists', methods=['GET'])
def search_playlists():
    if not sp:
        return jsonify({"error": "Spotify client is not connected."}), 400
    
    query = request.args.get('query', default='', type=str)
    if not query:
        return jsonify({"error": "Query parameter is required."}), 400

    try:
        liked_songs = get_liked_songs(sp)
        playlists = sp.search(q=query, type='playlist', limit=10)['playlists']['items']
        ranked_playlists = rank_playlists_by_liked_songs(sp, playlists, liked_songs)
        
        # Construct the response with additional playlist details
        playlist_data = [{
            "name": playlist['name'],
            "score": score,
            "link": playlist['external_urls']['spotify'],
            "thumbnail": playlist['images'][0]['url'] if playlist['images'] else None
        } for playlist, score in ranked_playlists]

        return jsonify({"playlists": playlist_data}), 200

    except SpotifyException as se:
        app.logger.error(f"Spotify API error: {str(se)}")
        return jsonify({"error": "Spotify API error occurred."}), 500
    except HTTPError as he:
        app.logger.error(f"HTTP error: {str(he)}")
        return jsonify({"error": "Network error occurred while fetching playlists."}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in /search_playlists endpoint: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500

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
    
def get_playlist_tracks(sp, playlist_id):
    try:
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        for item in results['items']:
            track = item['track']
            if track:
                tracks.append(track['id'])
        return tracks
    except SpotifyException as se:
        app.logger.error(f"Spotify API error in get_playlist_tracks: {str(se)}")
        raise
    except Exception as e:
        app.logger.error(f"Error getting tracks from playlist {playlist_id}: {str(e)}")
        raise
    
def rank_playlists_by_liked_songs(sp, playlists, liked_songs):
    try:
        playlist_scores = []
        for playlist in playlists:
            playlist_id = playlist['id']
            playlist_tracks = get_playlist_tracks(sp, playlist_id)
            common_tracks = set(liked_songs).intersection(playlist_tracks)
            score = len(common_tracks)
            playlist_scores.append((playlist, score))
        playlist_scores.sort(key=lambda x: x[1], reverse=True)
        return playlist_scores
    except Exception as e:
        app.logger.error(f"Error ranking playlists: {str(e)}")
        raise
    
if __name__ == '__main__':
    app.run(debug=True)