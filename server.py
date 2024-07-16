import socket
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication
import sys

# Import existing classes
from mainLAN import HomeScreen, GameController, Player, RealPlayer

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)  # Allow one client to connect
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"Connection from {self.client_address}")

        # Start a thread to handle client communication
        threading.Thread(target=self.handle_client).start()

    def handle_client(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if data:
                    self.process_client_data(data)
            except:
                print("Client disconnected")
                self.client_socket.close()
                break

    def process_client_data(self, data):
        print(f"Received from client: {data}")
        # Process the received data and update the game state accordingly
        # This is where you'll implement the logic to update the game based on client actions

    def send_to_client(self, data):
        self.client_socket.sendall(data.encode('utf-8'))

    def close(self):
        self.client_socket.close()
        self.server_socket.close()

def main():
    app = QApplication(sys.argv)
    server = Server('localhost', 5555)  # Replace with your desired IP and port
    home_screen = HomeScreen()
    home_screen.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
