import pygame
import sys
import socket
import select
import pygame.font
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([800, 600])

# Set up fonts
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 30)

# Networking setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))
client.setblocking(False)

players = []

def receive_messages():
    global players
    try:
        ready_to_read, _, _ = select.select([client], [], [], 0.1)
        if ready_to_read:
            message = client.recv(1024).decode('ascii')
            # Assuming it's a player list update
            players = message.split(',')
    except:
        pass

# Render Home Screen
def render_home_screen():
    screen.fill((0, 0, 0))  # Fill the background with black color
    textsurface = myfont.render('Welcome to the Card Game', False, (255, 255, 255))
    screen.blit(textsurface, (250, 250))
    pygame.display.flip()

# Render Lobby Screen
def render_lobby_screen(players):
    screen.fill((0, 0, 0))  # Fill the background with black color
    y = 50
    for player in players:
        textsurface = myfont.render(f'Player: {player}', False, (255, 255, 255))
        screen.blit(textsurface, (50, y))
        y += 50
    pygame.display.flip()

# Game states
HOME = 0
LOBBY = 1
GAME = 2

game_state = HOME

# Main loop
while True:
    receive_messages()  # Check for new messages
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    if game_state == HOME:
        render_home_screen()
        # Logic to switch to LOBBY state (not implemented here)
        # ...

    elif game_state == LOBBY:
        render_lobby_screen(players)
        # Logic to start the game (not implemented here)
        # ...

    elif game_state == GAME:
        # Render and handle game logic (not implemented here)
        # ...
        None

    pygame.time.wait(100)  # Add some delay to make the loop not run too fast
