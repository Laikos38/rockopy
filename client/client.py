import sys
sys.path.insert(1, "../")
import config
import socket
import time
import errno
import pickle


HEADER_LENGTH = 50
PORT = config.SERVER_PORT
IP = config.SERVER_IP


class Client:
    def __init__(self, username="USER"):
        self.username = username
        # Socket config
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.connection_tries = 0

    def wait_connection(self):
        self.connected = False
        print('Trying to connect to server...')
        while not self.connected:            
            if self.connection_tries < 10:                
                try:                    
                    self.client_socket.connect((IP, PORT))
                    #self.client_socket.setblocking(False)
                except Exception as e:
                    # print(type(e).__name__, e)
                    print('Retrying...')
                    time.sleep(5)
                    self.connection_tries += 1
                    continue
                
                self.send_command(self.username, False)
                print('Connected!')
                self.connected = True
            else:
                print("Can't connect to server after 10 tries.")
                sys.exit()

    def run(self):
        self.wait_connection()

    def wait_response(self):
        try:
            response_header = self.client_socket.recv(HEADER_LENGTH)
            if not len(response_header):
                print("Connection closed by the server.")
                sys.exit()
            response_length = int(response_header.decode('utf-8').strip())
            response = self.client_socket.recv(response_length)
            response = pickle.loads(response)
            return response

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error: {}'.format(str(e)))
            sys.exit()

    def send_command(self, command, wait):
        if command:
            command = pickle.dumps(command)
            command_header = bytes(f"{len(command):<{HEADER_LENGTH}}", 'utf-8')
            self.client_socket.send(command_header + command)
        if wait:
            return self.wait_response()


if __name__ == "__main__":
    client = Client()
    client.run()