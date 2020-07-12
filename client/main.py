import client
import threading
import sys
import os
import platform
import time
import signal


MAIN_MENU = 1
PLAYLIST_MENU = 2


class Main:
    def __init__(self):
        self.exit_app = False
        self.menu = MAIN_MENU
        self.client = None

    def start_client(self):
        self.client = client.Client(username=self.username)
        self.client_thread = threading.Thread(target=self.client.run, name='CLIENT')
        self.client_thread.start()

    def print_menu(self):
        if self.menu == MAIN_MENU:
            print("### MAIN MENU ###\n"
                  "1- Add song to rockopy.\n"
                  "2- View playlist.\n"
                  "q- Exit.\n>>>", end="")
        elif self.menu == PLAYLIST_MENU:
            print("### ROCKOPY PLAYLIST ###\n\nCurrently playing:")
            print(self.get_current_track_as_string())
            print("==================================================\n" + 
                  "\nRockopy playlist:")
            print(self.get_rockopy_playlist_as_string())
            print("\nb- Back.\n>>>", end="")

    def execute_option(self):
        option = input()
        if self.menu == MAIN_MENU:
            if option == "1":
                self.add_track_to_playlist()
            elif option == "2":
                self.menu = PLAYLIST_MENU
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

    def add_track_to_playlist(self):
        self.clscreen()
        query = input("Enter song/artist name to search: ")
        if query:
            response = self.client.send_command(["search_song", query], True)
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
                        self.client.send_command(["add_track_to_playlist", response['tracks'][selected_song-1]], False)
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
        response = self.client.send_command(['get_current_playback_data'], True)
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
        playlist = self.client.send_command(['get_playlist_tracks'], True)
        rtn = ''
        if playlist:
            count = 1
            for track in playlist:
                rtn += str(count) + ') ' + track['name'] + ' - ' + track['artist'] + '\n'
                count += 1
        else:
            rtn += 'The rockopy playlist is empty! Search and add songs!'
        return rtn

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
        self.username = input("Enter username: ")
        self.start_client()
        while not self.client.connected:
            if self.client.connection_tries < 10:
                continue
            else:
                sys.exit()
        while not self.exit_app:
            self.clscreen()
            if self.username:
                print("Username: " + self.username)
            self.print_menu()
            self.execute_option()


if __name__ == '__main__':
    main = Main()
    main.run()
    sys.exit()