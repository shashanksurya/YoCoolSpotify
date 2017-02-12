'''Views for YoCoolSpotify'''

from app import app
from flask import request,redirect,render_template,url_for
from spotipy import oauth2
from posix import access
import spotipy as spy
import json
from pprint import pprint

SPOTIPY_CLIENT_ID = 'd86cbb2a01764dc58683576dd59c87a9'
SPOTIPY_CLIENT_SECRET = '5736348bb2cd48328f5b2de93d435b1a'
SPOTIPY_REDIRECT_URI = 'http://localhost:6969/'
SCOPE = 'playlist-modify-private'
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE )

@app.route('/')
def main():
    access_token = ""
    token_info = sp_oauth.get_cached_token()
    
    if token_info:
        print("Found Cached Token")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Found Spotify Auth Code in requst URL")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']
    
    
    #Your token is active, you can fetch songs and return to user
    if access_token:
        print("Access token available")
        sp = spy.Spotify(access_token)
        results = sp.current_user()
        uri = 'spotify:user:12120746446:playlist:6ZK4Tz0ZsZuJBYyDZqlbGt'
        username = uri.split(":")[2]
        playlist_id = uri.split(":")[4]
        results = sp.user_playlist(username,playlist_id)
        ret_list = []
        for i, t in enumerate(results['tracks']['items']):
            temp = {}
            temp['img_url'] = t['track']['album']['images'][2]['url']
            temp['name'] = t['track']['name']
            temp['artist'] = t['track']['artists'][0]['name']
            temp['album'] = t['track']['album']['name']
            duration = int(t['track']['duration_ms'])/(1000*60)
            temp['duration'] = "{:2.2f}".format(duration)
            ret_list.append(temp)
            #ret_list.append(' '+str(i)+t['track']['name'])
        return render_template("index.html",songs=ret_list)
    else:
        return htmlForLoginButton()

@app.route("/addsong",methods=['GET','POST'])
def addsong():
    song = request.form['song']
    access_token = ""
    token_info = sp_oauth.get_cached_token()
    if token_info:
        print("Found Cached Token")
        access_token = token_info['access_token']
        sp = spy.Spotify(auth=access_token)
        sp.trace = False
        result = sp.search(song)
        track_id = [result['tracks']['items'][0]['uri']]
        #track_id = 'spotify:track:05uGBKRCuePsf43Hfm0JwX'
        #return str(track_id)
        results = sp.user_playlist_add_tracks("12120746446", "6ZK4Tz0ZsZuJBYyDZqlbGt",track_id)
        return redirect(url_for('main'))
    
    

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url