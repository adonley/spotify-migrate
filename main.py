import os
from flask import Flask, session, request, redirect, render_template, send_from_directory, Response, abort
from flask_session import Session
import spotipy
import uuid
import models
import json


app = Flask(__name__, template_folder=os.path.abspath('./templates'))
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    return caches_folder + session.get('uuid')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    scopes = [
        'playlist-read-collaborative',
        'playlist-read-private',
        'user-library-read',
        'user-follow-read',
        'playlist-modify-private',
        'playlist-modify-public',
        'user-follow-modify',
        'user-library-modify'
    ]
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=' '.join(scopes), cache_path=session_cache_path(), show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.get_cached_token():
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('signin.html', auth_url=auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return render_template('home.html', spotify_user=spotify.me()['display_name'])


@app.route('/sign_out', methods=['GET', 'POST'])
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def upload_playlist(user_id, sp, p: models.Playlist):
    # if public and not owned. Follow a playlist.
    if p.public and not p.owned:
        sp.current_user_follow_playlist(p.id)
        return

    # create playlist
    resp = sp.user_playlist_create(user_id, p.name, p.public, p.collaborative, p.description)

    # add tracks
    for chunk in divide_chunks([t.id for t in p.tracks], 30):
        sp.playlist_add_items(resp['id'], chunk)


@app.route('/import', methods=['POST'])
def import_account():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager)
    user_id = sp.me()['id']

    # check if the post request has the file part
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    # if user does not select file, browser also submit an empty part without filename
    if file.filename == '' or file is None:
        return 'No selected file'

    file_text = file.read()
    account_json = json.loads(file_text.decode('ascii'))

    # reverse here since we're trying to preserve order from other account
    playlists = [models.Playlist.from_json(p) for p in account_json['playlists']]
    playlists.reverse()
    for playlist in playlists:
        upload_playlist(user_id, sp, playlist)

    # API uses a put request under the hood. Max querystring for a lot of APIs is 1024 chars.
    # I'm not going to test what spotify is doing under the hood here, so let's just break it up.
    tracks = [models.Track.from_json(t).id for t in account_json['tracks']]
    tracks.reverse()
    for chunk in divide_chunks(tracks, 30):
        sp.current_user_saved_tracks_add(chunk)

    artists = [models.Artist.from_json(a).id for a in account_json['artists']]
    artists.reverse()
    for chunk in divide_chunks(artists, 30):
        sp.user_follow_artists(chunk)

    return 'SUCCESS'


@app.route('/export', methods=['GET'])
def export_account():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager)
    user_id = sp.me()['id']

    ret = {
        'playlists': [],
        'tracks': [],
        'artists': [],
        'user_id': user_id
    }

    # enumerate folled artists
    spotify_artists = sp.current_user_followed_artists()
    for spotify_artist in spotify_artists['artists']['items']:
        ret['artists'].append(models.Artist(spotify_artist).to_map())
    while spotify_artists['artists']['next'] is not None:
        spotify_artists = sp.next(spotify_artists['artists'])
        for spotify_artist in spotify_artists['artists']['items']:
            ret['artists'].append(models.Artist(spotify_artist).to_map())

    # enumerate tracks
    spotify_tracks = sp.current_user_saved_tracks()
    for spotify_track in spotify_tracks['items']:
        ret['tracks'].append(models.Track(spotify_track['track']).to_map())
    while spotify_tracks['next']:
        spotify_tracks = sp.next(spotify_tracks)
        for spotify_track in spotify_tracks['items']:
            ret['tracks'].append(models.Track(spotify_track['track']).to_map())

    # enumerate playlists
    spotify_playlists = sp.current_user_playlists()
    while spotify_playlists is not None:
        for spotify_playlist in spotify_playlists['items']:
            # create the playlist model
            playlist = models.Playlist(user_id, spotify_playlist)

            # we'll just re-follow when it's public and not owned
            if not playlist.owned and playlist.public:
                ret['playlists'].append(playlist.to_map())
                continue

            r = sp.playlist(spotify_playlist['id'], fields="tracks,next")

            spotify_tracks = r['tracks']
            for spotify_track in spotify_tracks['items']:
                playlist.add_track(spotify_track['track'])

            while spotify_tracks['next']:
                spotify_tracks = sp.next(spotify_tracks)
                for spotify_track in spotify_tracks['items']:
                    playlist.add_track(spotify_track['track'])

            ret['playlists'].append(playlist.to_map())

        if spotify_playlists['next']:
            spotify_playlists = sp.next(spotify_playlists)
        else:
            spotify_playlists = None
    return Response(
        json.dumps(ret),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=account_export.json"}
    )


if __name__ == '__main__':
    app.run(threaded=True, port=int(os.environ.get("PORT", 8080)), host='0.0.0.0')
