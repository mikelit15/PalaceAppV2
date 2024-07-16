import sys
import random
import time
import socket
import threading
import traceback
import pickle
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QLabel, QDialog, QGridLayout, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, \
    QTextEdit, QLineEdit
from PyQt6.QtGui import QFontMetrics, QPixmap, QIcon, QTransform, QPainter
from PyQt6.QtCore import Qt, QCoreApplication, QTimer
import qdarktheme

'''
Dark Mode QMessageBox Button Styling
'''
DarkB = ("""
    QPushButton {
        background-color: #0078D4; 
        color: #FFFFFF;           
        border: 1px solid #8A8A8A; 

    }
    QPushButton:hover {
        background-color: #669df2; 
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #80CFFF, stop:1 #004080);
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #004080, stop:1 #001B3D);
    }
""")

DarkNB = ("""
    QPushButton {
        color: #FFFFFF;          
    }
    QPushButton:hover {
        background-color: #669df2; 
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #80CFFF, stop:1 #004080);
    }
""")

# Dark Mode Styling
Dark = qdarktheme.load_stylesheet(
    theme="dark",
    custom_colors={
        "[dark]": {
            "primary": "#0078D4",
            "background": "#202124",
            "border": "#8A8A8A",
            "background>popup": "#252626",
        }
    },
) + """
    QMessageBox QLabel {
        color: #E4E7EB;
    }
    QDialog {
        background-color: #252626;
    }
    QComboBox:disabled {
        background-color: #1A1A1C; 
        border: 1px solid #3B3B3B;
        color: #3B3B3B;  
    }
    QPushButton {
    background-color: #0078D4; 
    color: #FFFFFF;           
    border: 1px solid #8A8A8A; 
    }
    QPushButton:hover {
        background-color: #669df2; 
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #80CFFF, stop:1 #004080);
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #004080, stop:1 #001B3D);
    }
    QPushButton:disabled {
        background-color: #202124; 
        border: 1px solid #3B3B3B;
        color: #FFFFFF;   
    }
"""

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
CARD_WIDTH = 56
CARD_HEIGHT = 84
BUTTON_WIDTH = 66
BUTTON_HEIGHT = 87

class HostLobby(QDialog):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setWindowTitle("Host Lobby")
        self.setGeometry(835, 400, 300, 200)
        self.server_thread = None
        self.client_socket = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.infoLabel = QLabel("Hosting Lobby...\nWaiting for players to join.")
        layout.addWidget(self.infoLabel)

        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        layout.addWidget(self.logText)

        self.startButton = QPushButton("Start Game")
        self.startButton.setEnabled(False)
        self.startButton.clicked.connect(self.startGame)
        layout.addWidget(self.startButton)

        backButton = QPushButton("Back")
        backButton.clicked.connect(self.backToOnlineDialog)
        layout.addWidget(backButton)

        self.setLayout(layout)
        self.startServer()

    def startServer(self):
        try:
            self.server_thread = threading.Thread(target=run_server)
            self.server_thread.start()
            self.logText.append("Server started, waiting for connections...")
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('127.0.0.1', 5555))
            threading.Thread(target=self.receive).start()
        except Exception as e:
            self.logText.append(f"Failed to start server: {e}")

    def receive(self):
        while True:
            try:
                message = pickle.loads(self.client_socket.recv(4096))
                if message['action'] == 'init':
                    self.game_state = message['game_state']
                    self.player_id = message['player_id']
                    self.logText.append(f'Connected as Player {self.player_id + 1}')
                    if len(self.game_state['hands']) == 2:
                        self.startButton.setEnabled(True)
                elif message['action'] == 'reject':
                    self.logText.append('Connection rejected: ' + message['reason'])
                else:
                    self.game_state = message
                    # Update game state in the UI
            except:
                self.logText.append('Connection lost!')
                self.client_socket.close()
                break

    def startGame(self):
        self.logText.append("Starting game...")
        self.main_window.startLANPalaceGame(self.client_socket, self.game_state, self.player_id)

    def backToOnlineDialog(self):
        if self.client_socket:
            self.client_socket.close()
        self.accept()
        self.main_window.playOnline()

class JoinLobby(QDialog):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setWindowTitle("Join Lobby")
        self.setGeometry(810, 375, 300, 200)
        self.client_socket = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.infoLabel = QLabel("Enter host address to join lobby:")
        layout.addWidget(self.infoLabel)

        self.addressInput = QLineEdit()
        self.addressInput.setPlaceholderText("Host IP Address")
        layout.addWidget(self.addressInput)

        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        layout.addWidget(self.logText)

        joinButton = QPushButton("Join Lobby")
        joinButton.clicked.connect(self.joinLobby)
        layout.addWidget(joinButton)

        backButton = QPushButton("Back")
        backButton.clicked.connect(self.backToOnlineDialog)
        layout.addWidget(backButton)

        self.setLayout(layout)

    def joinLobby(self):
        host_address = self.addressInput.text()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((host_address, 5555))
            self.logText.append(f"Connected to lobby at {host_address}")
            threading.Thread(target=self.receive).start()
        except Exception as e:
            self.logText.append(f"Failed to connect: {e}")

    def receive(self):
        while True:
            try:
                message = pickle.loads(self.client_socket.recv(4096))
                if message['action'] == 'init':
                    self.game_state = message['game_state']
                    self.player_id = message['player_id']
                    self.logText.append(f'Connected as Player {self.player_id + 1}')
                    if len(self.game_state['hands']) == 2:
                        self.main_window.startLANPalaceGame(self.client_socket, self.game_state, self.player_id)
                elif message['action'] == 'reject':
                    self.logText.append('Connection rejected: ' + message['reason'])
                else:
                    self.game_state = message
                    # Update game state in the UI
            except:
                self.logText.append('Connection lost!')
                self.client_socket.close()
                break

    def backToOnlineDialog(self):
        if self.client_socket:
            self.client_socket.close()
        self.accept()
        self.main_window.playOnline()

class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Palace')
        self.setWindowIcon(QIcon(r"_internal\palaceData\palace.ico"))
        self.setGeometry(660, 215, 600, 500)
        layout = QVBoxLayout()
        title = QLabel("Palace")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: bold;")
        layout.addWidget(title)

        buttonLayout = QVBoxLayout()

        buttonLayout.addWidget(QLabel(""))
        buttonLayout.addWidget(QLabel(""))

        playButton = QPushButton("Play")
        playButton.setFixedHeight(40)
        playButton.setFixedWidth(275)
        playButton.clicked.connect(self.showPlayerSelectionDialog)
        buttonLayout.addWidget(playButton)

        buttonLayout.addWidget(QLabel(""))

        onlineButton = QPushButton("Online")
        onlineButton.clicked.connect(self.playOnline)
        onlineButton.setFixedWidth(225)
        buttonLayout.addWidget(onlineButton, alignment=Qt.AlignmentFlag.AlignCenter)

        buttonLayout.addWidget(QLabel(""))
        
        rulesButton = QPushButton("Rules")
        rulesButton.clicked.connect(self.showRules)
        rulesButton.setFixedWidth(225)
        buttonLayout.addWidget(rulesButton, alignment=Qt.AlignmentFlag.AlignCenter)

        buttonLayout.addWidget(QLabel(""))

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(QCoreApplication.instance().quit)
        exitButton.setFixedWidth(225)
        buttonLayout.addWidget(exitButton, alignment=Qt.AlignmentFlag.AlignCenter)

        buttonLayout.addWidget(QLabel(""))

        buttonContainer = QWidget()
        buttonContainer.setLayout(buttonLayout)
        layout.addWidget(buttonContainer, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

    def cleanup(self):
        if hasattr(self, 'lanGameController'):
            self.lanGameController.cleanup()
            
    def startLANPalaceGame(self, client_socket, game_state, player_id):
        self.lanGameController = LANGameController(client_socket, game_state, player_id)
        self.lanGameController.startGame()

    def showPlayerSelectionDialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Number of Players")
        dialog.setGeometry(805, 350, 300, 200)

        layout = QVBoxLayout()

        label = QLabel("How many players?")
        layout.addWidget(label)

        self.radioGroup = QButtonGroup(dialog)
        radioButton2 = QRadioButton("Player vs. CPU")
        radioButton2.setFixedWidth(107)
        radioButton3 = QRadioButton("Player vs. CPU vs. CPU")
        radioButton3.setFixedWidth(150)
        radioButton4 = QRadioButton("Player vs. CPU vs. CPU vs. CPU")
        radioButton4.setFixedWidth(193)

        self.radioGroup.addButton(radioButton2, 2)
        self.radioGroup.addButton(radioButton3, 3)
        self.radioGroup.addButton(radioButton4, 4)

        layout.addWidget(radioButton2)
        layout.addWidget(radioButton3)
        layout.addWidget(radioButton4)
        layout.addWidget(QLabel(""))

        difficultyLabel = QLabel("Select AI Difficulty:")
        layout.addWidget(difficultyLabel)

        self.difficultyGroup = QButtonGroup(dialog)
        easyButton = QRadioButton("Easy")
        easyButton.setFixedWidth(55)
        mediumButton = QRadioButton("Medium")
        mediumButton.setFixedWidth(75)
        hardButton = QRadioButton("Hard")
        hardButton.setFixedWidth(57)
        impossibleButton = QRadioButton("Impossible")
        impossibleButton.setFixedWidth(115)

        self.difficultyGroup.addButton(easyButton, 1)
        self.difficultyGroup.addButton(mediumButton, 2)
        self.difficultyGroup.addButton(hardButton, 3)
        self.difficultyGroup.addButton(impossibleButton, 3)

        layout.addWidget(easyButton)
        layout.addWidget(mediumButton)
        layout.addWidget(hardButton)
        layout.addWidget(impossibleButton)
        layout.addWidget(QLabel(""))
        
        buttonBox = QHBoxLayout()
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")
        okButton.clicked.connect(lambda: self.startGameWithSelectedPlayers(dialog))
        cancelButton.clicked.connect(dialog.reject)
        buttonBox.addWidget(okButton)
        buttonBox.addWidget(cancelButton)
        layout.addLayout(buttonBox)

        dialog.setLayout(layout)
        dialog.exec()

    def startGameWithSelectedPlayers(self, dialog):
        numPlayers = self.radioGroup.checkedId()
        difficulty = self.difficultyGroup.checkedId()
        if numPlayers in [2, 3, 4]:
            dialog.accept()
            self.hide()
            difficulty_map = {1: 'easy', 2: 'medium', 3: 'hard'}
            difficulty_level = difficulty_map.get(difficulty, 'medium')
            controller = LANGameController(numPlayers, difficulty_level)  # Start game with selected number of players and difficulty level
            controller.view.show()

    def playOnline(self):
        self.onlineDialog = QDialog(self)
        self.onlineDialog.setWindowTitle("Online Multiplayer")
        self.onlineDialog.setGeometry(835, 400, 250, 150)
        layout = QVBoxLayout()

        hostButton = QPushButton("Host Lobby")
        hostButton.clicked.connect(lambda: self.hostLobby(self.onlineDialog))
        layout.addWidget(hostButton)

        layout.addWidget(QLabel())
        
        joinButton = QPushButton("Join Lobby")
        joinButton.clicked.connect(lambda: self.joinLobby(self.onlineDialog))
        layout.addWidget(joinButton)
        
        layout.addWidget(QLabel())

        closeButton = QPushButton("Close")
        closeButton.setFixedWidth(75)
        closeButton.clicked.connect(self.onlineDialog.accept)
        layout.addWidget(closeButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.onlineDialog.setLayout(layout)
        self.onlineDialog.exec()

    def hostLobby(self, onlineDialog):
        self.hostLobbyDialog = HostLobby(self, self)
        self.hostLobbyDialog.show()
        onlineDialog.accept()

    def joinLobby(self, onlineDialog):
        self.joinLobbyDialog = JoinLobby(self, self)
        self.joinLobbyDialog.show()
        onlineDialog.accept()
    
    def showRules(self):
        rulesDialog = QDialog(self)
        rulesDialog.setWindowTitle("Rules")
        rulesDialog.setGeometry(560, 100, 800, 300)
        rulesDialog.setWindowIcon(QIcon(r"_internal\palaceData\palace.ico"))
        layout = QVBoxLayout()
        rulesLabel = QLabel(
            """<h2>The Pack</h2>
        <ul>
            <li>2-4 players use one standard deck of 52 cards.</li>
        </ul>
        <h2>Rank of Cards</h2>
        <ul>
            <li>A-K-Q-J-9-8-7-6-5-4-3</li>
            <li>The 2 and 10 are special cards that reset the deck.</li>
            <li>The 7 is a special card that reverses the rank hierarchy, the next player ONLY must play a card rank 7 or lower.</li>
        </ul>
        <h2>Object of the Game</h2>
        <ul>
            <li>Play your cards in a pile using ascending order, and the first player to run out of cards wins.</li>
        </ul>
        <h2>The Deal</h2>
        <ul>
            <li>Deal three cards face down to each player. Players are not allowed to look at these cards and must place them
            face down in three columns in front of each player.</li>
            <li>Deal six cards to each player face down. Players may look at these cards in their hand.</li>
            <li>Players select three cards from their hand and place them face up on the three face down cards in front of them.
            Typically, higher value cards are placed face up.</li>
            <li>Place the remaining cards from the deck face down in the center of the table to form the Draw pile.</li>
        </ul>
        <h2>The Play</h2>
        <ul>
            <li>The player with the agreed worst average top cards is the first player and the second player is clockwise or counter clockwise
            with the second worst average top cards.</li>
            <li>The first player plays any card from their hand. You can play multiple cards on your turn, as long as they're all equal to or
            higher than the top pile card.</li>
            <li>Once you have have finished your turn, draw cards from the Draw pile to maintain three cards in your hand at all times.</li>
            <li>You must play a card if you can or pick up the current pile and add it to your hand.</li>
            <li>On their turn, a player can play any 2 card which resets the top pile card to 2, starting the sequence all over.</li>
            <li>On their turn, a player can play the 10 on any card, but it puts the pile into a bomb pile instead of resetting the sequence. The
            player who put the 10 down then draws up to three cards and plays any card.</li>
            <li>If four of the same rank are played in a row, either by one player or multiple players, it clears the pile. Place it in the bomb pile,
            as these cards are out of the game. The player that played the fourth card can then play any card from their hand.</li>
            <li>Play continues around the table until the deck is depleted.</li>
            <li>Once the deck is depleted, players rely solely on the cards in their hand. Keep playing until there are no cards left in your
            hand.</li>
            <li>When it's your turn and you don't have a hand, play one card from your face-up cards in front of you.</li>
            <li>When it's your turn and you've played all your face-up cards, pick a card that's face-down on the table. Don't look at it to choose.
            Simply flip it over. If it plays on the current card by being equal or higher, you can play it. If not, you must pick up the discard pile.</li>
            <li>If you pick up the discard pile, you must play those before continuing to play your face-down cards.</li>
            <li>First player to finish all cards in hand, face-up cards, and face-down cards, wins the game.</li>
        </ul>
        <ul>
            <li>
        </ul>
        """
        )
        rulesLabel.setTextFormat(Qt.TextFormat.RichText)
        rulesLabel.setWordWrap(True)
        rulesLabel.setFixedWidth(800)
        layout.addWidget(rulesLabel)
        closeButton = QPushButton("Close")
        closeButton.clicked.connect(rulesDialog.accept)
        layout.addWidget(closeButton)
        rulesDialog.setLayout(layout)
        rulesDialog.exec()

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.bottomCards = []
        self.topCards = []
        self.sevenSwitch = False  # Flag to restrict playable cards to 7 and lower or 2/10 for one turn

    def playCard(self, cardIndex, pile):
        card = self.hand.pop(cardIndex)
        if card[2]:
            card = (card[0], card[1], False, False)
        pile.append(card)
        return card

    def addToHand(self, cards):
        self.hand.extend(cards)

    def pickUpPile(self, pile):
        self.hand.extend(pile)
        pile.clear()

    def hasPlayableCards(self, topPile):
        if self.sevenSwitch:
            return any(VALUES[card[0]] <= 7 or card[0] in ['2', '10'] for card in self.hand)
        else:
            return any(card[0] == '2' or VALUES[card[0]] >= VALUES[topPile[-1][0]] for card in self.hand)

class RealPlayer(Player):
    def __init__(self, name, socket):
        super().__init__(name)
        self.socket = socket

    def send(self, data):
        try:
            self.socket.sendall(data.encode('utf-8'))
        except Exception as e:
            print(f"Error sending data: {e}")

    def receive(self):
        try:
            data = self.socket.recv(1024).decode('utf-8')
            return data
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None

class LANGameView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Palace Card Game')
        self.setWindowIcon(QIcon(r"_internal\palaceData\palace.ico"))
        self.setGeometry(250, 75, 500, 500)
        self.setFixedSize(1440, 900)

        self.layout = QGridLayout()

        # Player's Hand (Bottom)
        self.playerHandLabel = QLabel("Your Hand")
        self.playerHandLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.playerHandLayout = QHBoxLayout()
        self.topCardsLayout = QHBoxLayout()
        self.bottomCardsLayout = QHBoxLayout()

        self.playerContainer = QVBoxLayout()
        self.playerContainer.addLayout(self.bottomCardsLayout)
        self.playerContainer.addLayout(self.topCardsLayout)
        self.playerContainer.addWidget(self.playerHandLabel)
        self.playerContainer.addLayout(self.playerHandLayout)

        self.layout.addLayout(self.playerContainer, 8, 4)

        # Opponent's Hand (Top)
        self.opponentHandLabel = QLabel("Opponent's Hand")
        self.opponentHandLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.opponentHandLayout = QHBoxLayout()
        self.opponentTopCardsLayout = QHBoxLayout()
        self.opponentBottomCardsLayout = QHBoxLayout()

        self.opponentContainer = QVBoxLayout()
        self.opponentContainer.addLayout(self.opponentHandLayout)
        self.opponentContainer.addWidget(self.opponentHandLabel)
        self.opponentContainer.addLayout(self.opponentTopCardsLayout)
        self.opponentContainer.addLayout(self.opponentBottomCardsLayout)

        self.layout.addLayout(self.opponentContainer, 0, 4)

        # Center Console
        self.deckLabel = QLabel()
        self.deckLabel.setFixedWidth(190)
        self.deckLabel.setVisible(False)
        self.pileLabel = QLabel("\t     Select your 3 Top cards...")
        self.pileLabel.setStyleSheet("border: 0px solid black; background-color: transparent;")
        self.pickUpPileButton = QPushButton("Pick Up Pile")
        self.pickUpPileButton.setFixedWidth(125)
        self.pickUpPileButton.setVisible(False)
        self.pickUpPileButton.clicked.connect(self.controller.pickUpPile)
        self.currentPlayerLabel = QLabel("")

        spacer = QSpacerItem(60, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.consoleLayout = QHBoxLayout()
        self.consoleLayout.addWidget(self.deckLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.consoleLayout.addWidget(self.pileLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.consoleLayout.addItem(spacer)
        self.consoleLayout.addWidget(self.pickUpPileButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.centerLayout = QVBoxLayout()
        self.centerLayout.addWidget(QLabel(""))
        self.centerLayout.addWidget(self.currentPlayerLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.centerLayout.addLayout(self.consoleLayout)
        self.centerLayout.addWidget(QLabel(""))
        self.centerLayout.addWidget(QLabel(""))

        self.layout.addLayout(self.centerLayout, 4, 4)

        # Play card buttons layout
        self.confirmButton = QPushButton("Confirm")
        self.confirmButton.setEnabled(False)
        self.confirmButton.clicked.connect(self.confirmTopCardSelection)
        self.layout.addWidget(self.confirmButton, 10, 4)

        self.placeButton = QPushButton("Select A Card")
        self.placeButton.setEnabled(False)
        self.placeButton.clicked.connect(self.controller.placeCard)
        self.placeButton.setVisible(False)
        self.layout.addWidget(self.placeButton, 10, 4)

        self.setLayout(self.layout)

    def showTopCardSelection(self, player):
        self.chosenCards = []
        self.cardButtons = []
        self.updatePlayerHand(player.hand)

    def updatePlayerHand(self, hand):
        while self.playerHandLayout.count():
            item = self.playerHandLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for idx, card in enumerate(hand):
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            if not card[3]:
                pixmap = QPixmap(
                    fr"_internal\palaceData\cards\{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                button.setPixmap(pixmap)
            else:
                pixmap = QPixmap(r"_internal\palaceData\cards\back.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)

            button.mousePressEvent = lambda event, idx=idx, btn=button: self.selectTopCard(idx, btn)
            self.cardButtons.append(button)
            self.playerHandLayout.addWidget(button)

    def updateTopCardButtons(self, topCards, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for card in topCards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(
                f"_internal\palaceData\cards\{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button.setDisabled(True)
            layout.addWidget(button)

    def updatePlayerTopCards(self, topCards):
        self.updateTopCardButtons(topCards, self.topCardsLayout)

    def updateOpponentTopCards(self, topCards):
        self.updateTopCardButtons(topCards, self.opponentTopCardsLayout)

    def updateBottomCardButtons(self, bottomCards, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for card in bottomCards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(r"_internal\palaceData\cards\back.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(button)

    def updatePlayerBottomCards(self, bottomCards):
        self.updateBottomCardButtons(bottomCards, self.bottomCardsLayout)

    def updateOpponentBottomCards(self, bottomCards):
        self.updateBottomCardButtons(bottomCards, self.opponentBottomCardsLayout)

    def updateUI(self, currentPlayer, deckSize, pile):
        if self.controller.topCardSelectionPhase:
            self.currentPlayerLabel.setText(f"Select your 3 Top cards...")
            self.confirmButton.setEnabled(len(self.chosenCards) == 3)
        else:
            self.currentPlayerLabel.setText(f"Current Player: {currentPlayer.name}")

            if deckSize:
                self.deckLabel.setText(f"Draw Deck:\n\n{deckSize} cards remaining")
            else:
                self.deckLabel.setText("Draw Deck:\n\nEmpty")

            if pile:
                topCard = pile[-1]
                pixmap = QPixmap(fr"_internal/palaceData/cards/{topCard[0].lower()}_of_{topCard[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.pileLabel.setPixmap(pixmap)

            self.placeButton.setEnabled(len(self.controller.selectedCards) > 0)

    def revealCard(self, cardLabel, card):
        pixmap = QPixmap(fr"_internal/palaceData/cards/{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        cardLabel.setPixmap(pixmap)

    def showTopCardSelection(self, player):
        self.chosenCards = []
        self.cardButtons = []

    def selectTopCard(self, cardIndex, button):
        card = self.controller.players[0].hand[cardIndex]
        if (card, cardIndex) in self.chosenCards:
            self.chosenCards.remove((card, cardIndex))
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
        else:
            if len(self.chosenCards) < 3:
                self.chosenCards.append((card, cardIndex))
                button.setStyleSheet("border: 0px solid black; background-color: blue;")
        self.confirmButton.setEnabled(len(self.chosenCards) == 3)

    def confirmTopCardSelection(self):
        player = self.controller.players[0]
        for card, _ in self.chosenCards:
            player.topCards.append((card[0], card[1], True, False))
        for card, cardIndex in sorted(self.chosenCards, key=lambda x: x[1], reverse=True):
            del player.hand[cardIndex]
        self.updatePlayerTopCards(player.topCards)
        self.updatePlayerHand(player.hand)
        self.controller.proceedWithGameSetup()
        self.clearSelectionLayout()
        self.controller.topCardSelectionPhase = False
        self.confirmButton.setVisible(False)
        self.placeButton.setVisible(True)
        self.deckLabel.setVisible(True)
        self.currentPlayerLabel.setVisible(True)
        self.pickUpPileButton.setVisible(True)
        self.currentPlayerLabel.setText("Current Player: ")
        self.pileLabel.setText("Pile: Empty")
        self.pileLabel.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.controller.startGameLoop()

    def clearSelectionLayout(self):
        self.chosenCards = []
        self.cardButtons = []

    def setPlayerHandEnabled(self, enabled):
        for i in range(self.playerHandLayout.count()):
            widget = self.playerHandLayout.itemAt(i).widget()
            if widget:
                widget.setEnabled(enabled)

class LANGameController:
    def __init__(self, client_socket, game_state, player_id):
        self.client_socket = client_socket
        self.game_state = game_state
        self.player_id = player_id
        self.players = [RealPlayer(f"Player {i + 1}", None) for i in range(2)]
        self.currentPlayerIndex = self.game_state['turn']
        self.selectedCards = []
        self.playCardButtons = []
        self.topCardSelectionPhase = True
        self.view = None

    def startGame(self):
        self.startNetworkThread()
        self.view = LANGameView(self)
        self.view.show()
        self.view.showTopCardSelection(self.players[self.player_id])

    def startNetworkThread(self):
        threading.Thread(target=self.receive).start()

    def receive(self):
        while True:
            try:
                message = pickle.loads(self.client_socket.recv(4096))
                self.game_state = message
                self.updateUI()
            except:
                print('Connection lost!')
                self.client_socket.close()
                break

    def updateUI(self):
        currentPlayer = self.players[self.currentPlayerIndex]
        self.view.updateUI(currentPlayer, len(self.game_state['deck']), self.game_state['pile'])

    def sendMove(self, action, card=None):
        move = {'action': action}
        if card:
            move['card'] = card
        self.client_socket.send(pickle.dumps(move))

    def placeCard(self):
        player = self.players[self.currentPlayerIndex]
        playedCards = []
        for card, button in sorted(self.selectedCards, key=lambda x: player.hand.index(x[0])):
            playedCards.append(card)
            player.playCard(player.hand.index(card), self.game_state['pile'])
            self.view.revealCard(button, card)
            button.setParent(None)
            button.deleteLater()
        self.sendMove('play_card', playedCards)
        self.changeTurn()

    def drawCard(self):
        self.sendMove('draw_card')

    def changeTurn(self):
        self.currentPlayerIndex = (self.currentPlayerIndex + 1) % len(self.players)
        self.updateUI()

def run_server():
    import server  # Import and run the server script

def main():
    global scalingFactorWidth
    global scalingFactorHeight
    app = QApplication(sys.argv)
    app.setStyleSheet(Dark)
    screen = app.primaryScreen()
    screenSize = screen.size()
    screenWidth = screenSize.width()
    screenHeight = screenSize.height()
    scalingFactorWidth = screenWidth / 1920
    scalingFactorHeight = screenHeight / 1080
    homeScreen = HomeScreen()
    homeScreen.show()
    def cleanup():
        homeScreen.cleanup()
    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
