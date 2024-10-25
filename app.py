import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect
import pandas as pd


app = Flask(__name__)


app.secret_key = "secret"
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
TOKEN_INFO = "token_info"


@app.route('/')
def root():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', _external=True))


@app.route('/getTracks')
def getTracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for idx, item in enumerate(curGroup):
            track = item['track']
            val = track['name'] + " - " + track['artists'][0]['name']
            results += [val]
        if (len(curGroup) < 50):
            break
    
    df = pd.DataFrame(results, columns=["Saved songs:"]) 
    pd.set_option('display.colheader_justify', 'left')
    df = df.iloc[::-1]
    df.to_csv('songs.csv', index=False)

    a = pd.read_csv("songs.csv")
    a.to_html("Table.htm")
    html_file = a.to_html()
    return html_file


@app.route('/topTracks')
def topTracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_top_tracks(limit=50, offset=offset, time_range='medium_term')['items']
        for idx, item in enumerate(curGroup):
            track = item['name']
            album = item['album']
            albumpr = ""
            if (str(album['album_type']) == 'ALBUM'):
                albumpr = " - " + str(album['name'])
            artist = item['artists']
            val = track + " - " + str(artist[0]['name']) + albumpr
            results += [val]
        if (len(curGroup) < 50):
            break
    
    df = pd.DataFrame(results, columns=["Top songs for the last 6 months:"]) 
    pd.set_option('display.colheader_justify', 'left')
    df.to_csv('topsongs.csv', index=False)

    b = pd.read_csv("topsongs.csv")
    b.to_html("Table1.htm")
    html_file1 = b.to_html()
    return html_file1


@app.route('/topArtists')
def topArtists():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_top_artists(limit=50, offset=offset, time_range='medium_term')['items']
        for idx, item in enumerate(curGroup):
            artist = item['name']
            val = artist
            results += [val]
        if (len(curGroup) < 50):
            break
    
    df = pd.DataFrame(results, columns=["Top artists for the last 6 months:"]) 
    pd.set_option('display.colheader_justify', 'left')
    df.to_csv('topartists.csv', index=False)

    b = pd.read_csv("topartists.csv")
    b.to_html("Table2.htm")
    html_file2 = b.to_html()
    return html_file2


@app.route('/getPlaylists')
def getPlaylists():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_playlists(limit=50, offset=0)['items']
        for idx, item in enumerate(curGroup):
            playlist = item['name']
            val = playlist
            results += [val]
        if (len(curGroup) < 50):
            break
    
    df = pd.DataFrame(results, columns=["Playlists: "]) 
    pd.set_option('display.colheader_justify', 'left')
    df.to_csv('getPlaylists.csv', index=False)

    b = pd.read_csv("getPlaylists.csv")
    b.to_html("Table3.htm")
    html_file3 = b.to_html()
    return html_file3


@app.route('/getAlbums')
def getAlbums():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_saved_albums(limit=50, offset=0)['items']
        for idx, item in enumerate(curGroup):
            album = item['album']
            val = album['name'] + ' - ' + album['artists'][0]['name']
            results += [val]
        if (len(curGroup) < 50):
            break
    
    df = pd.DataFrame(results, columns=["Saved Albums: "]) 
    pd.set_option('display.colheader_justify', 'left')
    df.to_csv('getAlbums.csv', index=False)

    b = pd.read_csv("getAlbums.csv")
    b.to_html("Table4.htm")
    html_file4 = b.to_html()
    return html_file4


def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id="clientId",
            client_secret="clientSecret",
            redirect_uri=url_for('redirectPage', _external=True),
            scope="user-read-private")
