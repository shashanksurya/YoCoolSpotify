'''Views for YoCoolSpotify'''

from app import app
from app import constants
from flask import request, redirect, render_template, url_for, session
from spotipy import oauth2
from posix import access
import spotipy as spy
import json
import httplib2
import os
import sys
import random
import re

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
    
    if access_token and youtube:
        spotify_playlist_list = getCurrentSpotifyPlaylistList()
        youtube_playlist_list = getCurrentYoutubePlaylistList() 
        return render_template("index.html", songs=youtube_playlist_list)
    else:
        #todo always falls back to spotify
        return htmlForLoginButton()


@app.route('/user')
def user():
    spotify_playlist_list = getCurrentSpotifyPlaylistList()
    youtube_playlist_list = getCurrentYoutubePlaylistList()     
    return render_template("user.html", songs=youtube_playlist_list)

@app.route("/addsong", methods=['POST'])
def addsong():
    song_query = request.form['song']
    source = request.form['source']
    #print(source)
    if source == "spotify":
        access_token = getSpotifyToken()
        sp = spy.Spotify(auth=access_token)
        sp.trace = False
        result = sp.search(song_query)
        track_id = [result['tracks']['items'][0]['uri']]
        results = sp.user_playlist_add_tracks("12120746446", "6ZK4Tz0ZsZuJBYyDZqlbGt", track_id)
    elif source == "youtube":
        video_query_response = getYoutubeVideo(song_query) 
        if video_query_response is not None:
            video = [x for x in video_query_response.split("$$")]
            addYoutubeVideo(video[1])
    return redirect(url_for('user'))
    
@app.route("/youtubeOAuth2Callback")
def youtubeOauth2Callback():
    url = request.url
    print(url)


def getSpotifyToken():
    access_token = ""
    token_info = sp_oauth.get_cached_token()
    if token_info:
        print("Found Cached Token")
        access_token = token_info['access_token']
    return access_token

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
                                   scope=constants.YOUTUBE_READ_WRITE_SCOPE,
                                   redirect_uri='http://localhost:8080/')
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
    
def getYoutubeVideo(query):
    youtube = initYoutube()
    search_response = youtube.search().list(
        q=query,
        part = "id,snippet",
        maxResults=3
        ).execute() 
    
    videos = []
    for search_result in search_response.get("items",[]):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s$$%s" % (search_result["snippet"]["title"],
                search_result["id"]["videoId"]))

    #print(videos)
    if len(videos)>0:
        return videos[0]


def getCurrentSpotifyPlaylistList():
    ret_list = []
    access_token = getSpotifyToken()
    if access_token:
        sp = spy.Spotify(access_token)
        results = sp.current_user()
        uri = 'spotify:user:12120746446:playlist:6ZK4Tz0ZsZuJBYyDZqlbGt'
        username = uri.split(":")[2]
        playlist_id = uri.split(":")[4]
        results = sp.user_playlist(username, playlist_id)
        for i, t in enumerate(results['tracks']['items']):
            temp = {}
            temp['img_url'] = t['track']['album']['images'][2]['url']
            temp['name'] = t['track']['name']
            temp['artist'] = t['track']['artists'][0]['name']
            temp['album'] = t['track']['album']['name']
            duration = int(t['track']['duration_ms']) / (1000 * 60)
            temp['duration'] = "{:2.2f}".format(duration)
            ret_list.append(temp)

    return ret_list

def getCurrentYoutubePlaylistList():
    #keep dicts of videos in ret_list
    ret_list = []

    youtube = initYoutube()
    playlistitems_list_request = youtube.playlistItems().list(
                playlistId=constants.YOUTUBE_PLAYLIST_ID,
                part="snippet,contentDetails",
            maxResults=30
            )

    playlistitems_list_response = playlistitems_list_request.execute()
    #print(playlistitems_list_response)
    for playlist_item in playlistitems_list_response['items']:
        video_dict = {}
        #print(playlist_item)
        video_dict['name'] = playlist_item['snippet']['title']
        video_dict['img_url'] = playlist_item['snippet']['thumbnails']['default']['url']
        video_dict['artist'] = "--"
        video_dict['album'] = "--"
        video_dict['duration'] = "--:--"
        ret_list.append(video_dict)
    return ret_list



def addYoutubeVideo(video_id):
    youtube = initYoutube()

    playlist_add_request = youtube.playlistItems().insert(
        part="snippet",
        body=dict(
            snippet={
                'playlistId':constants.YOUTUBE_PLAYLIST_ID,
                'resourceId': {
                    'kind':'youtube#video',
                    'videoId':video_id
                    }
                }
            )
        ).execute()
