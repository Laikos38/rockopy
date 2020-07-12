from sys import path
path.insert(1, "../")
import config
import os, platform
import spotipy
import spotipy.oauth2
from server import Server
from threading import Thread
from random import randint
import spotipyHandler
import renewableTimer


LOGIN_MENU = 0
MAIN_MENU = 1
PLAYLIST_MENU = 2
PLAYBACK_MENU = 3
TRACKS_TO_SEARCH = config.TRACKS_TO_SEARCH


class Main:
    def __init__(self):
        self.menu = LOGIN_MENU
        self.spotipyHandler = None
        self.exit_app = False
        self.username = None
        self.spotipyObject = None
        self.server = None
        self.playback_timer = renewableTimer.RenewableTimer()
        self.playback_state = None

    def print_menu(self):
        if self.menu == LOGIN_MENU:
            print("### LOGIN ###\n\n"
                  "1) Log in.\n"
                  "q) Exit.\n>>>", end="")
        elif self.menu == MAIN_MENU:
            print("### MAIN MENU ###\n\n"
                  "1) Start playing music from rockopy playlist.\n"
                  "2) Add song to the rockopy playlist.\n"
                  "3) View rockopy playlist.\n"
                  "4) Add/change a fill playlist.\n"
                  "5) View available devices.\n"
                  "6) View user data.\n"
                  "7) View server info.\n"
                  "q) Exit.\n>>>", end="")
        elif self.menu == PLAYLIST_MENU:
            print("### ROCKOPY PLAYLIST ###\n\nCurrently playing:")
            print(self.get_current_track_as_string())
            print("==================================================\n" + 
                  "\nRockopy playlist:")
            print(self.get_rockopy_playlist_as_string())
            print("\nb) Back.\n>>>", end="")
        elif self.menu == PLAYBACK_MENU:
            print("### ROCKOPY PLAYBACK ###\n\nCurrently playing:")
            print(self.get_current_track_as_string())
            print("==================================================\n" + 
                "\nFill playlist:")
            if self.server.is_fill_playlist_exists():
                print(self.server.get_fill_playlist()['name'] + "\n")
            else:
                print("You didn't especify a fill playlist. If you start the rockopy "
                    "player and the rockopy playlist is empty, a random track of "
                    "the fill playlist it's gonna start instead.\n")
            print("==================================================\n" + 
                "\nRockopy playlist:")
            print(self.get_rockopy_playlist_as_string())
            print("==================================================\n")
            print("\n1) Play.\n"
                "2) Pause.\n"
                "3) Next track.\n"
                "4) Previous track.\n"
                "5) Add song to the rockopy playlist.\n"
                "6) Add/change a fill playlist.\n"
                "r) Refresh.\n"
                "b) Back.\n>>>", end="")

    def execute_option(self):
        option = input()
        if self.menu == LOGIN_MENU:
            if option == "1":
                self.login()
            elif option == "q":
                self.exit_app = True
            else:
                print("ERROR. Invalid option.")
                self.screen_pause()
        elif self.menu == MAIN_MENU:
            if option == "1":
                if self.server.is_device_selected():
                    self.menu = PLAYBACK_MENU
                else:
                    device = self.select_device()
                    if not device:
                        self.menu = MAIN_MENU
                    else:
                        self.menu = PLAYBACK_MENU
            elif option == "2":
                self.add_track_to_playlist()
            elif option == "3":
                self.menu = PLAYLIST_MENU
            elif option == "4":
                self.add_fill_playlist()
            elif option == "5":
                self.clscreen()
                self.print_current_user_devices()
            elif option == "6":
                self.clscreen()
                self.print_current_user_data()
            elif option == "7":
                self.get_server_info()
            elif option == "q":
                self.exit_app = True
            else:
                print("ERROR. Invalid option.")
                self.screen_pause()
        elif self.menu == PLAYLIST_MENU:
            if option == "b":
                self.menu = MAIN_MENU
            else:
                print("ERROR. Invalid option.")
                self.screen_pause()
        elif self.menu == PLAYBACK_MENU:
            if option == "1":
                self.start_playback()
            elif option == "2":
                self.pause()
            elif option == "3":
                self.next_track()
            elif option == "4":
                self.prev_track()
            elif option == "5":
                self.add_track_to_playlist()
            elif option == "6":
                self.add_fill_playlist()
            elif option == "r":
                pass
            elif option == "b":
                self.menu = MAIN_MENU
            else:
                print("ERROR. Invalid option.")
                self.screen_pause()

    def login(self):
        self.clscreen()
        self.server = Server()
        try:
            self.spotipyObject = self.server.login_to_spotify()
        except Exception as ex:
            print("\n\nERROR during login process.\n" + str(ex) + "\n")
        if self.spotipyObject:
            server_thread = Thread(target=self.server.run, name='SERVER')
            server_thread.start()
            self.spotipyHandler = spotipyHandler.SpotipyHandler(self.spotipyObject)
            self.menu = MAIN_MENU
        self.screen_pause()

    def add_track_to_playlist(self):
        self.clscreen()
        query = input("Enter song/artist name to search: ")
        if query:
            try:
                response = self.server.search_song(query)
            except Exception as ex:
                print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
                self.screen_pause()
                return
            if response:
                self.clscreen()
                print("Results for '" + query + "':\n")
                count = 1
                for track in response['tracks']:
                    print(str(count) + ")\n\t" + 
                          "Name: " + track['name'] + "\n\t" +
                          "Artist: " + track['artist'] + "\n\t" +
                          "Album: " + track['album'])
                    count += 1
                print("\nb) Back.")
                print("\nSelect a song to add to the playlist\n>>>", end="")
                selected_song = input()
                if selected_song == "b":
                    return
                if selected_song and selected_song.isdigit():
                    selected_song = int(selected_song)
                    if selected_song in range(1, count):
                        selected_song = int(selected_song)
                        self.server.add_track_to_rockopy_playlist(response['tracks'][selected_song-1])
                        self.clscreen()
                        print(response['tracks'][selected_song-1]['name'] + " added to the rockopy playlist!")
                        self.screen_pause()
                        return
                print("ERROR. Invalid option.")
                self.screen_pause()
            else:
                print("No results.")
                self.screen_pause()

    def get_current_track_as_string(self):
        try:
            response = self.server.get_current_track()
        except Exception as ex:
            print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
            self.screen_pause()
            return
        if response:
            rtn = "\t" + response['name'] + " by " + response['artist'] + "\n"
            rtn += "\t" + "Playing in " + response['device'] + "\n"
            rtn += "\t" + "Suffle: "
            if response['shuffle']:
                rtn += "ON\n"
            else:
                rtn += "OFF\n"    
            return rtn 
        else:
            return "Spotify player is paused!\n"

    def get_rockopy_playlist_as_string(self):
        try:
            playlist = self.server.get_rockopy_playlist()
        except Exception as ex:
            print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
            self.screen_pause()
            return
        rtn = ''
        if playlist:
            count = 1
            for track in playlist:
                rtn += str(count) + ') ' + track['name'] + ' - ' + track['artist'] + '\n'
                count += 1
        else:
            rtn += 'The rockopy playlist is empty! Search and add songs!\n'
        return rtn

    def get_server_info(self):
        self.clscreen()
        print(self.server.get_server_info_as_string())
        self.screen_pause()

    def print_current_user_data(self):
        try:
            user_data = self.server.get_current_user_data()
        except Exception as ex:
            print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
            self.screen_pause()
            return
        rtn = "Current user data:\n\t"
        rtn += "Name: " + user_data['display_name'] + "\n\t"
        rtn += "ID: " + user_data['id'] + "\n\t"
        if 'profile_pic' in user_data:
            rtn += "Profile pic: " + user_data['profile_pic']
        print(rtn)
        self.screen_pause()

    def print_current_user_devices(self):
        try:
            devices = self.server.get_user_devices()
        except Exception as ex:
            print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
            self.screen_pause()
            return
        count = 1
        rtn = ""
        if devices['devices']:
            for device in devices['devices']:
                rtn += str(count) + ")\n\t"
                rtn += "Name: " + device['name'] + "\n\t"
                rtn += "Type: " + device['type'] + "\n"
                count += 1
        else:
            rtn += "No active devices found! Open Spotify to connect Rockopy!"
        print(rtn)
        self.screen_pause()

    def add_fill_playlist(self):
        self.clscreen()
        try:
            user_playlists = self.server.get_user_playlists()
        except Exception as ex:
            print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
            self.screen_pause()
            return
        if user_playlists['playlists']:
            print("If you start the rockopy player and the rockopy playlist is empty, "
              "a random track of the fill playlist i gonna start instead.\n\n")
            count = 1
            print("Select one of your playlists:\n")
            for playlist in user_playlists['playlists']:
                print(str(count) + ") " + playlist['name'])
                count += 1
            print("b) Back.")
            print("\nSelect a playlist\n>>>", end="")
            selected_playlist = input()
            if selected_playlist == "b":
                return
            if selected_playlist and selected_playlist.isdigit():
                selected_playlist = int(selected_playlist)
                if selected_playlist in range(1, count):
                    selected_playlist = int(selected_playlist)
                    self.server.set_fill_playlist(user_playlists['playlists'][selected_playlist-1])
                    self.clscreen()
                    print(user_playlists['playlists'][selected_playlist-1]['name'] + " added as fill playlist!")
                    self.screen_pause()
                    return
            print("ERROR. Invalid option.")
            self.screen_pause()
        else:
            print("Nothing to show! You don't have any playlist saved on your Spotify Music Library!")
            self.screen_pause()

    def start_playback(self, signum=None, frame=None, track=None):
        if self.playback_state == False and self.playback_state is not None:
            try:
                self.server.start_playback()
            except Exception as ex:
                print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
                self.screen_pause()
                return
            self.playback_timer.resume()
            self.playback_state = True
            return
        if not track:
            track = self.determine_next_track()
            if not track:
                self.clscreen()
                print("Nothing to play! Rockopy playlist is empty and you didn't set a fill playlist!\n")
                self.screen_pause()
                return
        try:
            prev_track = self.server.get_current_track()
        except Exception as ex:
            print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
            self.screen_pause()
            return
        if prev_track:
            try:
                self.server.set_prev_track(prev_track)
            except Exception as ex:
                print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
                self.screen_pause()
                return
        try:
            self.server.start_playback(uris=[track['uri']])
        except Exception as ex:
            print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
            self.screen_pause()
            return
        if self.playback_timer.isActive:
            self.playback_timer.cancel()
        self.playback_timer.set_timer(track['duration_ms']//1000, self.start_playback)
        self.playback_timer.start()
        self.clscreen()
        self.print_menu()

    def select_device(self):
        self.clscreen()
        try:
            devices = self.server.get_user_devices()
        except Exception as ex:
            print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
            self.screen_pause()
            return
        count = 1
        if devices['devices']:
            for device in devices['devices']:
                print(str(count) + ")\n\t" + 
                      "Name: " + device['name'] + "\n\t" + 
                      "Type: " + device['type'] + "\n")
                count += 1
        else:
            print("No active devices found! Open Spotify to connect Rockopy!")
            self.screen_pause()
            return False
        print("\nSelect a device to play\n>>>", end="")
        selected_device = input()
        if selected_device and selected_device.isdigit():
            selected_device = int(selected_device)
            if selected_device in range(1, count):
                self.server.set_device(devices['devices'][selected_device-1])
                return devices['devices'][selected_device-1]
        print("\nERROR. Invalid option.")
        self.screen_pause()
        return False

    def determine_next_track(self):
        if self.server.is_rockopy_playlist_empty() and self.server.is_fill_playlist_exists():
            try:
                track = self.server.get_random_track_from_fill_playlist()
            except Exception as ex:
                print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
                self.screen_pause()
                return
        elif not self.server.is_rockopy_playlist_empty():
            try:
                track = self.server.get_track_from_rockopy_playlist()
            except Exception as ex:
                print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
                self.screen_pause()
                return
        elif self.server.is_rockopy_playlist_empty() and not self.server.is_fill_playlist_exists():
            track = False
        return track

    def next_track(self):
        if not self.playback_state:
            self.playback_state = True
        if self.playback_timer:
            self.playback_timer.cancel()
        self.start_playback()

    def prev_track(self):
        if not self.playback_state:
            self.playback_state = True
        try:
            if self.server.is_prev_track_exists():
                if self.playback_timer:
                    self.playback_timer.cancel()
                prev_track = self.server.get_prev_track()
                self.start_playback(track=prev_track)
            else:
                self.clscreen()
                print("Nothing to play! No previous tracks played found.\n")
                self.screen_pause()
                return
        except Exception as ex:
            print("\n\nERROR:\n" + str(ex) + "\nPlease try again later.\n")
            self.screen_pause()
            return
    
    def pause(self):
        if self.playback_state:
            self.playback_state = False
            self.server.pause_playback()
            self.playback_timer.pause()

    def clscreen(self):
        if platform.system() == "Windows":
            os.system("cls")
        elif platform.system() == "Linux":
            os.system("clear")
        elif platform.system() == "Darwin":
            os.system("clear")
        else:
            print("\n" * 20)

    def screen_pause(self):
        input("\n\nPress ENTER key to continue...")

    def run(self):
        while not self.exit_app:
            self.clscreen()
            if self.username:
                print("Usuario: " + self.username)
            self.print_menu()
            self.execute_option()


def run():
    main = Main()
    main.run()
    os._exit(1)


if __name__ == '__main__':
    run()