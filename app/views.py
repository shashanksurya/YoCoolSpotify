'''Views for YoCoolSpotify'''

from app import app
from app import constants
from flask import request, redirect, render_template, url_for
from spotipy import oauth2
from posix import access
import spotipy as spy
import json
import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from pprint import pprint


sp_oauth = oauth2.SpotifyOAuth(constants.SPOTIPY_CLIENT_ID, constants.SPOTIPY_CLIENT_SECRET, \
                                constants.SPOTIPY_REDIRECT_URI, scope=constants.SCOPE, \
                                cache_path=constants.CACHE)

@app.route('/')
def main():
    # init spotify
    access_token = getSpotifyToken()
    # init youtube
    youtube = initYoutube()
    #return youtube_token
    # Code to Write
    # Your token is active, you can fetch songs and return to user
    if access_token:
        print("Access token available")
        sp = spy.Spotify(access_token)
        results = sp.current_user()
        uri = 'spotify:user:12120746446:playlist:6ZK4Tz0ZsZuJBYyDZqlbGt'
        username = uri.split(":")[2]
        playlist_id = uri.split(":")[4]
        results = sp.user_playlist(username, playlist_id)
        ret_list = []
        for i, t in enumerate(results['tracks']['items']):
            temp = {}
            temp['img_url'] = t['track']['album']['images'][2]['url']
            temp['name'] = t['track']['name']
            temp['artist'] = t['track']['artists'][0]['name']
            temp['album'] = t['track']['album']['name']
            duration = int(t['track']['duration_ms']) / (1000 * 60)
            temp['duration'] = "{:2.2f}".format(duration)
            ret_list.append(temp)
            # ret_list.append(' '+str(i)+t['track']['name'])
        return render_template("index.html", songs=ret_list)
    else:
        return htmlForLoginButton()

@app.route("/addsong", methods=['POST'])
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
        # track_id = 'spotify:track:05uGBKRCuePsf43Hfm0JwX'
        # return str(track_id)
        results = sp.user_playlist_add_tracks("12120746446", "6ZK4Tz0ZsZuJBYyDZqlbGt", track_id)
        return redirect(url_for('main'))
    
@app.route("/youtubeOAuth2Callback")
def youtubeOauth2Callback():
    url = request.url
    print(url)
    

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

def initYoutube():
    flow = flow_from_clientsecrets(constants.YOUTUBE_CLIENT_SECRETS_FILE,\
                                   message=constants.MISSING_CLIENT_SECRETS_MESSAGE,\
                                   scope=constants.YOUTUBE_READ_WRITE_SCOPE)
    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()
    
    if credentials is None or credentials.invalid:
        flags = argparser.parse_args()
        credentials = run_flow(flow, storage, flags)
    else:
        print("Found valid oauth2 json")
    
    youtube = build(constants.YOUTUBE_API_SERVICE_NAME, constants.YOUTUBE_API_VERSION,
                    http=credentials.authorize(httplib2.Http()))
    print("Done authentication with Youtube")
    return youtube


def getYoutubeToken():
    access_token = ""
    authSubUrl = getYoutubeauthURL()
    return '<a href="%s">Login to your Google account</a>' % authSubUrl
        
    
def getSpotifyToken():
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
    return access_token
    
