from sys import path
path.insert(1, "../")
import config
import socket
import threading
import select
import spotipyHandler
import pickle


HEADER_LENGTH = 50
PORT = config.SERVER_PORT
IP = config.SERVER_IP
TEST = False


class Server:
    def __init__(self, host=IP, port=PORT):
        self.client_count = 0
        self.host = host
        self.port = port

        # Socket config
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket_list = [self.server_socket]
        self.clients = {}

        # Handler for spotipy querys
        self.spotipyHandler = spotipyHandler.SpotipyHandler()

        if TEST:
            print("Server is up and listening for clients.")

    def login_to_spotify(self):
        return self.spotipyHandler.login()
    
    def receive_msg(self, client_socket):
        try:
            msg_header = client_socket.recv(HEADER_LENGTH)
            if not len(msg_header):
                return False
            
            msg_length = int(msg_header.decode('utf-8').strip())
            msg = client_socket.recv(msg_length)
            msg = pickle.loads(msg)
            return {"header": msg_header, "data": msg}

        except:
            return False

    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        while True:
            read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list)

            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    client_socket, client_addr = self.server_socket.accept()
                    user = self.receive_msg(client_socket)['data']
                    if user is False:
                        continue
                    self.socket_list.append(client_socket)
                    self.clients[client_socket] = user
                    self.client_count += 1
                    if TEST:
                        print("New client " + user + " connected! Addr: " + client_addr[0])
                else:
                    msg = self.receive_msg(notified_socket)

                    if msg is False:
                        if TEST:
                            print("Client " + self.clients[notified_socket] + " has disconnected.")
                        self.socket_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        self.client_count -= 1
                        continue
                    
                    command = msg['data']
                    self.execute_command(command, notified_socket)
            
            for notified_socket in exception_sockets:
                self.socket_list.remove(notified_socket)
                del self.clients[notified_socket]
                self.client_count -= 1

    def execute_command(self, command, socket_to_respond):
        if command[0] == "search_song":
            response = self.spotipyHandler.search_song(command[1])
            self.send_respond(response, socket_to_respond)
        elif command[0] == "get_playlist_tracks":
            response = self.get_rockopy_playlist()
            self.send_respond(response, socket_to_respond)
        elif command[0] == "get_user_playlists":
            response = self.spotipyHandler.get_user_playlists()
            self.send_respond(response, socket_to_respond)
        elif command[0] == "add_track_to_playlist":
            self.add_track_to_rockopy_playlist(command[1])
        elif command[0] == "create_playlist":
            self.spotipyHandler.create_playlist(command[1], command[2], command[3])
        elif command[0] == "get_current_playback_data":
            response = self.get_current_track()
            self.send_respond(response, socket_to_respond)
        else:
            self.send_respond('Command error.', socket_to_respond)

    def send_respond(self, response, socket_to_respond):
        response = pickle.dumps(response)
        response_header = bytes(f"{len(response):<{HEADER_LENGTH}}", 'utf-8')
        socket_to_respond.send(response_header + response)

    def get_server_info_as_string(self):
        rtn = ""
        rtn += "Server host: " + str(self.host) + "\n"
        rtn += "Server port: " + str(self.port) + "\n"
        rtn += "Clients count: " + str(self.client_count) + "\n"
        rtn += "Clients:\n"
        count = 1
        for key, value in self.clients.items():
            rtn += '\t' + str(count) + ') User: ' + value + ' - Socket: ' + str(key.getsockname()) + '\n'
            count += 1
        return rtn

    def search_song(self, query):
        return self.spotipyHandler.search_song(query)
    
    def add_track_to_rockopy_playlist(self, track):
        self.spotipyHandler.add_track_to_rockopy_playlist(track)

    def get_current_track(self):
        return self.spotipyHandler.get_current_playback_data()

    def get_rockopy_playlist(self):
        return self.spotipyHandler.playlist

    def get_current_user_data(self):
        return self.spotipyHandler.get_current_user_data()

    def get_user_devices(self):
        return self.spotipyHandler.get_user_devices()

    def get_user_playlists(self):
        return self.spotipyHandler.get_user_playlists()

    def set_fill_playlist(self, playlist):
        self.spotipyHandler.set_fill_playlist(playlist)

    def is_fill_playlist_exists(self):
        return self.spotipyHandler.is_fill_playlist_exists()

    def get_fill_playlist(self):
        return self.spotipyHandler.get_fill_playlist()

    def is_rockopy_playlist_empty(self):
        return self.spotipyHandler.playlist == []

    def set_device(self, device):
        self.spotipyHandler.set_device(device)

    def start_playback(self, context_uri=None, uris=None, offset=None):
        self.spotipyHandler.start_playback(context_uri, uris, offset)

    def is_device_selected(self):
        return self.spotipyHandler.is_device_selected()

    def get_track_from_rockopy_playlist(self):
        return self.spotipyHandler.get_track_from_rockopy_playlist()

    def get_random_track_from_fill_playlist(self):
        return self.spotipyHandler.get_random_track_from_fill_playlist()
    
    def is_next_track_exists(self):
        return self.spotipyHandler.is_next_track_exists()

    def get_next_track(self):
        return self.spotipyHandler.get_next_track()
    
    def is_prev_track_exists(self):
        return self.spotipyHandler.is_prev_track_exists()

    def get_prev_track(self):
        prev_tracks = self.spotipyHandler.get_prev_tracks()
        if prev_tracks:
            prev_track = prev_tracks[-1]
            self.spotipyHandler.previous_tracks.remove(prev_track)
        return prev_track

    def set_prev_track(self, prev_track):
        self.spotipyHandler.set_prev_track(prev_track)

    def set_next_track(self, next_track):
        self.spotipyHandler.set_next_track(next_track)

    def pause_playback(self):
        self.spotipyHandler.pause_playback()


if __name__ == "__main__":
    TEST = True
    server = Server()
    server.run()