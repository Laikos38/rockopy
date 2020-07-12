from sys import path
path.insert(1, '../')
import config
import renewableTimer
import spotipy
from spotipy import oauth2
import os
import fnmatch
import json
import time
import webbrowser
from random import randint


TRACKS_TO_SEARCH = config.TRACKS_TO_SEARCH


class SpotipyHandler:
    def __init__(self, spotipyObject=None):
        self.spotipyObject = spotipyObject
        self.token = None
        self.playlist = []
        self.device = None
        self.fill_playlist = None
        self.next_track = None
        self.previous_tracks = []
        self.token_timer = renewableTimer.RenewableTimer()

    def login(self):
        users_history = {}
        # search directory for cached users.
        c = 1
        for file_name in os.listdir('.'):
            if fnmatch.fnmatch(file_name, '.cache-*'):
                users_history[c] = file_name[7:]
                c += 1

        if len(users_history) != 0:
            c = 1
            print("### LOGIN ###\n\nLogin: ")
            for user_key in users_history:
                print(str(user_key) + ") " + users_history[user_key])
                c += 1
            print(str(len(users_history) + 1) + ") Login with other user.")
            print("b) Back.")
            print(">>>", end="")
            option = input()

            if option == 'b':
                return None
            if option and option.isdigit():
                option = int(option)
                if 0 < option <= len(users_history):
                    with open(".cache-" + users_history[option]) as json_auth:
                        token_info = json.load(json_auth)
                        self.username = users_history[option]
                        # If the token is expired, its refreshed
                        if self.is_token_expired(token_info):
                            self.refresh()
                        else:
                            self.token = token_info['access_token']
                        self.spotipyObject = spotipy.Spotify(auth=self.token)
                        self.set_refresh_token_alarm()
                        return self.spotipyObject
                elif option == len(users_history) + 1:
                    return self.login_new_user()
            print("\nERROR. Invalid option.\n\n")
            return
        else:
            # if there is not previous logged users cache files
            return self.login_new_user()

    def login_new_user(self):
        self.username = input("Enter spotify username: ")
        sp_oauth = oauth2.SpotifyOAuth(
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            redirect_uri=config.REDIRECT_URI,
            scope='user-read-playback-state ' +
                    'user-modify-playback-state ' +
                    'user-read-currently-playing ' + 
                    'streaming ' +
                    'app-remote-control ' +
                    'playlist-modify-public ' +
                    'playlist-read-private ' + 
                    'playlist-modify-private',
            cache_path=".cache-" + self.username
        )
        auth_url = sp_oauth.get_authorize_url()
        webbrowser.open(auth_url)
        response = input("Paste the auth link here (http://rockopy/?code=...): ")

        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)

        self.token = token_info['access_token']
        self.spotipyObject = spotipy.Spotify(auth=self.token)
        self.set_refresh_token_alarm()
        return self.spotipyObject

    def is_token_expired(self, token_info):
        now = int(time.time())
        return token_info['expires_at'] - now < 60

    def refresh(self):
        with open(".cache-" + self.username) as json_auth:
            token_info = json.load(json_auth)
        sp_oauth = oauth2.SpotifyOAuth(
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            redirect_uri=config.REDIRECT_URI,
            scope='user-read-playback-state ' +
                    'user-modify-playback-state ' +
                    'user-read-currently-playing ' + 
                    'streaming ' +
                    'app-remote-control ' +
                    'playlist-modify-public ' +
                    'playlist-read-private ' + 
                    'playlist-modify-private',
            cache_path=".cache-" + self.username
        )
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        self.token = token_info['access_token']
        self.spotipyObject = spotipy.Spotify(auth=self.token)
        self.set_refresh_token_alarm()
        return self.spotipyObject

    def set_refresh_token_alarm(self):
        self.token_timer.set_timer(1300, self.refresh)
        self.token_timer.start()

    def get_current_user_data(self):
        user_data = self.spotipyObject.current_user()
        rtn = {}
        rtn['display_name'] = user_data['display_name']
        rtn['id'] = user_data['id']
        if user_data["images"]:
            rtn['profile_pic'] = user_data["images"][0]["url"]
        return rtn

    def search_song(self, query):
        tracks_results = self.spotipyObject.search(q=query, limit=TRACKS_TO_SEARCH)
        # tracks_results = json.dumps(tracks_results, sort_keys=True, indent=4)
        tracks_results = tracks_results['tracks']['items']
        rtn = {'tracks': []}
        for track in tracks_results:
            aux = {}
            aux['name'] = track['name']
            aux['artist'] = track['artists'][0]['name']
            aux['album'] = str(track['album']['name']) + " (" + str(track['album']['release_date'][:4]) + ")"
            aux['uri'] = track['uri']
            aux['id'] = track['id']
            aux['duration_ms'] = track['duration_ms']
            rtn['tracks'].append(aux)
        return rtn

    def add_track_to_rockopy_playlist(self, track):
        self.playlist.append(track)

    def get_track(self, song_id):
        track = self.spotipyObject.track(song_id)
        rtn ={}
        rtn['name'] = track['name']
        rtn['artist'] = track['artists'][0]['name']
        rtn['album'] = str(track['album']['name']) + " (" + str(track['album']['release_date'][:4]) + ")"
        rtn['duration_ms'] = track['duration_ms']
        rtn['uri'] = track['uri']
        return rtn

    def get_playlist_tracks(self, playlist_id):
        user_id = self.get_current_user_data()['id']
        playlist_tracks = self.spotipyObject.user_playlist_tracks(user_id, playlist_id)
        playlist_tracks = playlist_tracks['items']
        rtn = {}
        rtn['tracks'] = []
        for track in playlist_tracks:
            aux = {}
            aux['id'] = track['track']['id']
            aux['uri'] = track['track']['uri']
            aux['name'] = track['track']['name']
            aux['duration_ms'] = track['track']['duration_ms']
            aux['artist'] = track['track']['artists'][0]['name']
            rtn['tracks'].append(aux)
        return rtn

    def create_playlist(self, name, public, description):
        user_id = self.get_current_user_data()['id']
        self.spotipyObject.user_playlist_create(user_id, name, public, description)

    def get_user_playlists(self):
        playlists_data = self.spotipyObject.current_user_playlists()
        playlists_data = playlists_data['items']
        rtn = {'playlists': []}
        for playlist in playlists_data:
            aux = {}
            aux['id'] = playlist['id']
            aux['uri'] = playlist['uri']
            aux['name'] = playlist['name']
            aux['description'] = playlist['description']
            aux['number_of_tracks'] = playlist['tracks']['total']
            rtn['playlists'].append(aux)
        return rtn

    def get_user_devices(self):
        devices_results = self.spotipyObject.devices()
        devices_results = devices_results['devices']
        rtn = {'devices': []}
        for device in devices_results:
            aux = {}
            aux['id'] = device['id']
            aux['name'] = device['name']
            aux['type'] = device['type']
            aux['active'] = device['is_active']
            rtn['devices'].append(aux)
        return rtn

    def get_current_playback_data(self):
        response = self.spotipyObject.current_playback()
        if response:
            rtn = {}
            rtn['device'] = response['device']['name'] + " (" + response['device']['type'] + ")"
            rtn['shuffle'] = response['shuffle_state']
            rtn['name'] = response['item']['name']
            rtn['artist'] = response['item']['artists'][0]['name']
            rtn['uri'] = response['item']['uri']
            rtn['id'] = response['item']['id']
            rtn['duration_ms'] = response['item']['duration_ms']
            return rtn
        else:
            return False

    def start_playback(self, context_uri_=None, uris_=None, offset_=None):
        if context_uri_ is not None:
            self.spotipyObject.start_playback(self.device['id'], context_uri=context_uri_, offset=offset_)
        if uris_ is not None:
            self.spotipyObject.start_playback(self.device['id'], uris=uris_, offset=offset_)
        else:
            self.spotipyObject.start_playback()

    def pause_playback(self):
        self.spotipyObject.pause_playback()

    def set_fill_playlist(self, playlist):
        self.fill_playlist = playlist

    def get_fill_playlist(self):
        return self.fill_playlist

    def is_fill_playlist_exists(self):
        if self.fill_playlist:
            return True
        return False

    def set_device(self, device):
        self.device = device

    def is_device_selected(self):
        if self.device:
            return True
        return False

    def get_track_from_rockopy_playlist(self):
        track = self.playlist[0]
        self.playlist.remove(track)
        return track

    def get_random_track_from_fill_playlist(self):
        user_id = self.get_current_user_data()['id']
        random_track = self.spotipyObject.user_playlist_tracks(
            user_id, 
            playlist_id=self.fill_playlist['id'], 
            fields=None, 
            limit=1, 
            offset=randint(1, self.fill_playlist['number_of_tracks']-1), 
        )
        random_track = random_track['items'][0]['track']
        return random_track

    def is_next_track_exists(self):
        if self.next_track:
            return True
        return False

    def is_prev_track_exists(self):
        if self.previous_tracks:
            return True
        return False
    
    def set_next_track(self, next_track):
        self.next_track = next_track

    def set_prev_track(self, prev_track):
        self.previous_tracks.append(prev_track)

    def get_next_track(self):
        return self.next_track

    def get_prev_tracks(self):
        return self.previous_tracks