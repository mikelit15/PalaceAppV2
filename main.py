import sys
import random
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QCoreApplication, QTimer
import qdarktheme

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
        playButton.setFixedHeight(45)
        playButton.setFixedWidth(250)
        playButton.clicked.connect(self.startGame)
        buttonLayout.addWidget(playButton)

        buttonLayout.addWidget(QLabel(""))
        buttonLayout.addWidget(QLabel(""))

        rulesButton = QPushButton("Rules")
        rulesButton.clicked.connect(self.showRules)
        buttonLayout.addWidget(rulesButton)

        buttonLayout.addWidget(QLabel(""))

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(QCoreApplication.instance().quit)
        buttonLayout.addWidget(exitButton)

        buttonLayout.addWidget(QLabel(""))

        buttonContainer = QWidget()
        buttonContainer.setLayout(buttonLayout)
        buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(buttonContainer)

        self.setLayout(layout)

    def startGame(self):
        self.hide()
        controller = GameController(2)  # Start game with 2 players
        controller.view.show()

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


class AIPlayer(Player):
    def __init__(self):
        super().__init__("AI")

    def playTurn(self, pile, deckSize, playerTopCards):
        if not pile:
            return [min(self.hand, key=lambda card: VALUES[card[0]])]
        
        if all(card[3] for card in self.hand):
            return [random.choice(self.hand)]
        
        validCards = [card for card in self.hand if self.isCardPlayable(card, pile)]

        if not validCards:
            return -1

        # Use 2s and 10s as a last resort
        nonSpecialCards = [card for card in validCards if card[0] not in ['2', '10']]
        if nonSpecialCards:
            validCards = nonSpecialCards

        # Sort valid cards: prefer lower cards earlier and higher cards later in the game
        validCards.sort(key=lambda card: VALUES[card[0]])

        # Play higher-value cards if the deck is nearly empty or if the opponent has fewer cards
        if deckSize < 5 or len(playerTopCards) < 3:
            validCards.sort(key=lambda card: -VALUES[card[0]])

        # Always play 7s if there is a strategic advantage
        sevens = [card for card in validCards if card[0] == '7']
        if sevens:
            return sevens
        
        # Choose the best card to play based on the sorted valid cards
        bestCard = validCards[0]
        return [bestCard]

    def isCardPlayable(self, card, pile):
        topCard = pile[-1] if pile else None
        if self.sevenSwitch:
            return VALUES[card[0]] <= 7 or card[0] in ['2', '10']
        if not topCard:
            return True  # Any card is playable if the pile is empty
        return card[0] == '2' or card[0] == '10' or VALUES[card[0]] >= VALUES[topCard[0]]

    def chooseTopCards(self):
        sortedHand = sorted(self.hand, key=lambda card: VALUES[card[0]])
        for card in sortedHand[:3]:
            self.topCards.append((card[0], card[1], True, False))
        self.hand = sortedHand[3:]


class GameView(QWidget):
    global scalingFactorWidth
    global scalingFactorHeight

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.playCardButtons = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Palace Card Game')
        self.setWindowIcon(QIcon(r"_internal\palaceData\palace.ico"))
        self.setGeometry(560, 115, 2000, 500)
        self.setFixedSize(800, 800)

        self.layout = QVBoxLayout()

        # AI player's hand
        self.AIHandLayout = QHBoxLayout()
        self.layout.addLayout(self.AIHandLayout)
        self.AIPlayerLabel = QLabel("AI Player's Hand")
        self.AIPlayerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.AIPlayerLabel)

        # AI player's top cards
        self.AITopCardsLayout = QHBoxLayout()
        self.layout.addLayout(self.AITopCardsLayout)

        # AI player's bottom cards
        self.AIBottomCardsLayout = QHBoxLayout()
        self.layout.addLayout(self.AIBottomCardsLayout)

        # Draw deck, Pile, and Pick Up Pile button layout
        center = QHBoxLayout()
        center.setSpacing(0)  # Set spacing to 0 to remove padding between widgets
        center.setContentsMargins(0, 0, 0, 0)  # Remove margins around the layout
        self.deckLabel = QLabel()  # Initialize the deck label
        self.deckLabel.setFixedWidth(150)
        self.deckLabel.setVisible(False)
        center.addWidget(self.deckLabel)
        self.pileLabel = QLabel("Select your 3 Top cards...")
        self.pileLabel.setStyleSheet("border: 0px solid black; background-color: transparent;")
        self.pileLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(self.pileLabel)
        self.pickUpPileButton = QPushButton("Pick Up Pile")
        self.pickUpPileButton.setFixedWidth(150)
        self.pickUpPileButton.setVisible(False)
        self.pickUpPileButton.clicked.connect(self.controller.pickUpPile)
        center.addWidget(self.pickUpPileButton)
        self.layout.addLayout(center)

        # Current player label
        self.currentPlayerLabel = QLabel("")
        self.currentPlayerLabel.setVisible(False)
        self.currentPlayerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.currentPlayerLabel)

        # Player's bottom cards
        self.bottomCardsLayout = QHBoxLayout()  # Initialize bottom cards layout for the player
        self.layout.addLayout(self.bottomCardsLayout)

        # Player's top cards
        self.topCardsLayout = QHBoxLayout()  # Initialize top cards layout for the player
        self.layout.addLayout(self.topCardsLayout)

        # Player's hand
        self.playerHandLabel = QLabel("Player's Hand")
        self.playerHandLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.playerHandLabel)
        self.playerHandLayout = QHBoxLayout()
        self.layout.addLayout(self.playerHandLayout)

        # Play card buttons layout
        self.playButtonsLayout = QHBoxLayout()  # Initialize the layout for play buttons
        self.layout.addLayout(self.playButtonsLayout)

        self.confirmButton = QPushButton("Confirm")
        self.confirmButton.setEnabled(False)
        self.confirmButton.clicked.connect(self.confirmTopCardSelection)
        self.layout.addWidget(self.confirmButton)

        self.placeButton = QPushButton("Select A Card")
        # self.placeButton.setFixedWidth(300)
        self.placeButton.setEnabled(False)
        self.placeButton.clicked.connect(self.controller.placeCard)
        self.placeButton.setVisible(False)

        self.layout.addWidget(self.placeButton)

        self.setLayout(self.layout)

    def updateHand(self, hand, layout, isPlayer=True):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if isPlayer:
            self.controller.playCardButtons = []

        for idx, card in enumerate(hand):
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            if not card[3]:  # Check if isBottomCard is False
                pixmap = QPixmap(
                    fr"_internal\palaceData\cards\{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                button.setPixmap(pixmap)
            else:
                pixmap = QPixmap(r"_internal\palaceData\cards\back.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if isPlayer:
                if self.controller.topCardSelectionPhase:
                    button.mousePressEvent = lambda event, idx=idx, btn=button: self.selectTopCard(idx, btn)
                else:
                    try:
                        button.mousePressEvent = lambda event, idx=idx, btn=button: self.controller.prepareCardPlacement(idx, btn)
                    except IndexError:
                        return
                self.controller.playCardButtons.append(button)
            layout.addWidget(button)

    def updatePlayerHand(self, hand):
        self.updateHand(hand, self.playerHandLayout, isPlayer=True)

    def updateAIHand(self, hand):
        self.updateHand(hand, self.AIHandLayout, isPlayer=False)

    def updateTopCardButtons(self, topCards):
        for i in reversed(range(self.topCardsLayout.count())):
            self.topCardsLayout.itemAt(i).widget().deleteLater()

        for card in topCards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(f"_internal\palaceData\cards\{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button.setDisabled(True)
            self.topCardsLayout.addWidget(button)

    def updateBottomCardButtons(self, bottomCards):
        for i in reversed(range(self.bottomCardsLayout.count())):
            self.bottomCardsLayout.itemAt(i).widget().deleteLater()

        for card in bottomCards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(r"_internal\palaceData\cards\back.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bottomCardsLayout.addWidget(button)

    def updateAITopCardButtons(self, topCards):
        for i in reversed(range(self.AITopCardsLayout.count())):
            self.AITopCardsLayout.itemAt(i).widget().deleteLater()

        for card in topCards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(f"_internal/palaceData/cards/{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setDisabled(True)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.AITopCardsLayout.addWidget(button)

    def updateAIBottomCardButtons(self, bottomCards):
        for i in reversed(range(self.AIBottomCardsLayout.count())):
            self.AIBottomCardsLayout.itemAt(i).widget().deleteLater()

        for card in bottomCards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(r"_internal\palaceData\cards\back.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.AIBottomCardsLayout.addWidget(button)

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
        self.updateTopCardButtons(player.topCards)
        self.updatePlayerHand(player.hand)
        self.controller.proceedWithGameSetup()
        self.clearSelectionLayout()
        self.controller.topCardSelectionPhase = False
        self.confirmButton.setVisible(False)
        self.placeButton.setVisible(True)
        self.deckLabel.setVisible(True)
        self.currentPlayerLabel.setVisible(True)
        self.pickUpPileButton.setVisible(True)
        self.pileLabel.setText("Pile: Empty")
        self.pileLabel.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.controller.startGameLoop()  # Start the game loop after top card selection
        self.updateAIHand(self.controller.players[1].hand)  # Immediately update the AI hand display

    def clearSelectionLayout(self):
        self.chosenCards = []
        self.cardButtons = []
        
    def setPlayerHandEnabled(self, enabled):
        for i in range(self.playerHandLayout.count()):
            widget = self.playerHandLayout.itemAt(i).widget()
            if widget:
                widget.setEnabled(enabled)

    # def getCardFront(cardSuit, cardRank, width=CARD_WIDTH, height=CARD_HEIGHT):
    #     print(cardSuit)
    #     print(cardRank)
    #     return QPixmap(f"_internal/palaceData/cards/{cardSuit.lower()}_of_{cardRank.lower()}.png").scaled(
    #         width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    # def getCardBack(width=CARD_WIDTH, height=CARD_HEIGHT):
    #     return QPixmap(r"_internal\palaceData\cards\back.png").scaled(
    #         width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)


class GameController:
    def __init__(self, numPlayers):
        self.view = GameView(self)
        self.numPlayers = numPlayers
        self.players = []
        self.deck = []
        self.pile = []
        self.currentPlayerIndex = 0
        self.selectedCards = []  # Track the selected cards and their buttons
        self.playCardButtons = []  # Initialize playCardButtons
        self.topCardSelectionPhase = True  # Flag for top card selection phase
        self.setupGame()

    def startGameLoop(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.gameLoop)
        self.timer.start(1000)  # Run the game loop every second

    def gameLoop(self):
        currentPlayer = self.players[self.currentPlayerIndex]
        if isinstance(currentPlayer, AIPlayer):
            self.AIPlayTurn()
        else:
            self.view.updateUI(currentPlayer, len(self.deck), self.pile)

    def pickUpPile(self):
        top = False
        if self.pile == []:
            return
        currentPlayer = self.players[self.currentPlayerIndex]
        pickedUpCards = self.pile[:]
        currentPlayer.pickUpPile(self.pile)
        print(f"{currentPlayer.name} picks up the pile")
        self.view.pileLabel.setText("Pile: Empty")
        currentPlayer.sevenSwitch = False
        # Update hand to reveal any picked-up bottom cards
        for card in pickedUpCards:
            if card[3]:  # if isBottomCard is True
                if card in currentPlayer.hand:
                    index = currentPlayer.hand.index(card)
                    currentPlayer.hand[index] = (card[0], card[1], card[2], False)  # Reveal the card in the hand
                    if index < self.view.playerHandLayout.count():
                        self.view.revealCard(self.view.playerHandLayout.itemAt(index).widget(), card)  # Reveal the card
        for card in reversed(currentPlayer.hand):
            if card[2]:
                currentPlayer.topCards.append(currentPlayer.hand.pop(currentPlayer.hand.index(card)))
                top = True
        if top:
            if isinstance(currentPlayer, AIPlayer):
                self.view.updateAITopCardButtons(currentPlayer.topCards)
            else:
                self.view.updateTopCardButtons(currentPlayer.topCards)
        self.view.setPlayerHandEnabled(False)
        self.view.placeButton.setText("AI Turn...")
        self.updateUI()
        self.changeTurn()
        
    def setupGame(self):
        self.players.append(Player("Player"))
        for _ in range(self.numPlayers - 1):
            self.players.append(AIPlayer())
        self.deck = self.createDeck()
        random.shuffle(self.deck)
        self.dealInitialCards()
        self.view.updatePlayerHand(self.players[0].hand)
        self.view.showTopCardSelection(self.players[0])

    def proceedWithGameSetup(self):
        for AIPlayer in self.players[1:]:
            AIPlayer.chooseTopCards()
            self.view.updateAITopCardButtons(AIPlayer.topCards)
            self.view.updateAIBottomCardButtons(AIPlayer.bottomCards)
        self.view.updateBottomCardButtons(self.players[0].bottomCards)
        self.topCardSelectionPhase = False
        self.updateUI()
        self.startGameLoop()  # Start the game loop after top card selection

    def createDeck(self):
        # suits = ['clubs', 'spades']
        suits = ['diamonds', 'hearts', 'clubs', 'spades']
        return [(rank, suit, False, False) for rank in RANKS for suit in suits]  # Adding isBottomCard as False

    def dealInitialCards(self):
        for player in self.players:
            player.bottomCards = [(card[0], card[1], False, True) for card in self.deck[:3]]  # Set isBottomCard to True
            player.hand = self.deck[3:9]
            self.deck = self.deck[9:]

    def updateUI(self):
        currentPlayer = self.players[self.currentPlayerIndex]
        if not self.topCardSelectionPhase:
            self.view.updateUI(currentPlayer, len(self.deck), self.pile)
            if isinstance(currentPlayer, AIPlayer):
                self.view.placeButton.setText("AI Turn...")
                self.view.updateAIHand(currentPlayer.hand)
                self.view.pickUpPileButton.setDisabled(True)
            else:
                self.view.placeButton.setText("Select A Card")
                self.view.pickUpPileButton.setDisabled(False)
                self.view.updatePlayerHand(currentPlayer.hand)
                if not self.topCardSelectionPhase:
                    self.updatePlayableCards()

    def prepareCardPlacement(self, cardIndex, cardLabel):
        card = self.players[self.currentPlayerIndex].hand[cardIndex]
        if (card, cardLabel) in self.selectedCards:
            self.selectedCards.remove((card, cardLabel))
            cardLabel.setStyleSheet("border: 0px solid black; background-color: transparent;")  # Unhighlight the deselected card
        else:
            self.selectedCards.append((card, cardLabel))
            cardLabel.setStyleSheet("border: 0px solid black; background-color: blue;")  # Highlight selected card
        # Enable all buttons with the same rank, disable the rest
        selectedCardRank = card[0]
        if not self.selectedCards:
            for i, lbl in enumerate(self.playCardButtons):
                handCard = self.players[self.currentPlayerIndex].hand[i]
                if handCard[3] or self.isCardPlayable(handCard):  # Always enable bottom cards
                    lbl.setEnabled(True)
        else:
            for i, lbl in enumerate(self.playCardButtons):
                handCard = self.players[self.currentPlayerIndex].hand[i]
                if handCard[0] == selectedCardRank or (handCard, lbl) in self.selectedCards:
                    lbl.setEnabled(True)
                elif not handCard[3]:  # Disable only non-bottom cards
                    lbl.setEnabled(False)
        self.view.placeButton.setEnabled(len(self.selectedCards) > 0)  # Enable place button if any card is selected
        if self.view.placeButton.text() == "Place":
            self.view.placeButton.setText("Select A Card")
        else:
            self.view.placeButton.setText("Place")

    def isCardPlayable(self, card):
        topCard = self.pile[-1] if self.pile else None
        if self.players[self.currentPlayerIndex].sevenSwitch:
            return VALUES[card[0]] <= 7 or card[0] in ['2', '10']
        if not topCard:
            return True  # Any card is playable if the pile is empty
        return card[0] == '2' or card[0] == '10' or VALUES[card[0]] >= VALUES[topCard[0]]

    def placeCard(self):
        player = self.players[self.currentPlayerIndex]
        playedCards = []
        pickUp = False

        for card, button in sorted(self.selectedCards, key=lambda x: player.hand.index(x[0])):
            if card[3] and not self.isCardPlayable(card):
                print(card)
                playedCards.append(card)
                for i, card in enumerate(playedCards):
                    self.pile.append(player.hand.pop(player.hand.index(playedCards[i])))
                    self.pile[-1] = (card[0], card[1], card[2], False)  # Set isBottomCard to False
                    self.view.revealCard(button, card)
                pickUp = True
                button.setParent(None)  # Immediately remove the button from its parent
                button.deleteLater()  # Schedule it for deletion
            else:
                playedCards.append(card)
                for i, card in enumerate(playedCards):
                    if card[3]:  # Check if it's a bottom card
                        playedCards[i] = (card[0], card[1], card[2], False)  # Set isBottomCard to False
                player.playCard(player.hand.index(card), self.pile)
                self.view.revealCard(button, card)
                button.setParent(None)  # Immediately remove the button from its parent
                button.deleteLater()  # Schedule it for deletion
            
        if pickUp:    
            topCard = self.pile[-1]
            pixmap = QPixmap(fr"_internal/palaceData/cards/{topCard[0].lower()}_of_{topCard[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.view.pileLabel.setPixmap(pixmap)
            QCoreApplication.processEvents()
            time.sleep(1.5)      
            self.pickUpPile()
            for card in reversed(player.hand):
                if card[3]:
                    player.bottomCards.append(player.hand.pop(player.hand.index(card)))
            self.view.updatePlayerHand(player.hand)
            self.view.updateBottomCardButtons(player.bottomCards)
            self.view.setPlayerHandEnabled(False)
            self.view.placeButton.setText("AI Turn...")
            return

        self.selectedCards = []  # Clear selected cards
        print(f"{player.name} plays {', '.join([f'{card[0]} of {card[1]}' for card in playedCards])}")

        # Draw cards if fewer than 3 in hand
        while len(player.hand) < 3 and self.deck:
            player.hand.append(self.deck.pop(0))

        self.view.updatePlayerHand(player.hand)  # Update the player hand layout

        # Update the state of playable cards
        self.updatePlayableCards()

        # Check if 4 cards of the same rank in a row have been played
        if self.checkFourOfAKind():
            print("Four of a kind! Clearing the pile.")
            self.pile.clear()
            self.view.pileLabel.setText("Bombed")
            self.updateUI()
            gameOver = self.checkGameState()
            return

        if '2' in [card[0] for card in playedCards]:
            self.players[self.currentPlayerIndex].sevenSwitch = False
            topCard = self.pile[-1]
            pixmap = QPixmap(fr"_internal/palaceData/cards/{topCard[0].lower()}_of_{topCard[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.view.pileLabel.setPixmap(pixmap)
            self.updateUI()
            gameOver = self.checkGameState()
            if gameOver:
                return
        elif '10' in [card[0] for card in playedCards]:
            self.pile.clear()
            self.players[self.currentPlayerIndex].sevenSwitch = False
            self.view.pileLabel.setText("Bombed")
            self.updateUI()
            gameOver = self.checkGameState()
            if gameOver:
                return
        else:
            if '7' in [card[0] for card in playedCards]:
                self.players[(self.currentPlayerIndex + 1) % len(self.players)].sevenSwitch = True
            else:
                self.players[(self.currentPlayerIndex + 1) % len(self.players)].sevenSwitch = False
            self.view.placeButton.setEnabled(False)
            topCard = self.pile[-1]
            pixmap = QPixmap(fr"_internal/palaceData/cards/{topCard[0].lower()}_of_{topCard[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.view.pileLabel.setPixmap(pixmap)
            self.updateUI()
            gameOver = self.checkGameState()
            if gameOver:
                return
            self.changeTurn()
            self.view.setPlayerHandEnabled(False)
            self.view.placeButton.setText("AI Turn...")

    def AIPlayTurn(self):
        time.sleep(0.5)
        AIPlayer = self.players[self.currentPlayerIndex]
        playerTopCards = self.players[0].topCards  # Assuming player is always the first in the list
        playedCards = []
        pickUp = False

        # Get cards to play
        cardsToPlay = AIPlayer.playTurn(self.pile, len(self.deck), playerTopCards)

        if cardsToPlay == -1:
            self.pickUpPile()
            return
        
        for card in cardsToPlay:
            cardIndex = AIPlayer.hand.index(card)
            cardLabel = self.view.AIHandLayout.itemAt(cardIndex).widget()
            if card[3] and not self.isCardPlayable(card):
                playedCards.append(card)
                for i, card in enumerate(playedCards):
                    self.pile.append(AIPlayer.hand.pop(AIPlayer.hand.index(playedCards[i])))
                    self.pile[-1] = (card[0], card[1], card[2], False)  # Set isBottomCard to False
                    self.view.revealCard(cardLabel, card)
                pickUp = True
                cardLabel.setParent(None)  # Immediately remove the button from its parent
                cardLabel.deleteLater()  # Schedule it for deletion
            else:
                playedCards.append(card)
                self.pile.append(AIPlayer.hand.pop(AIPlayer.hand.index(card)))
                self.pile[-1] = (card[0], card[1], False, False)  # Set isBottomCard to False
                self.view.revealCard(cardLabel, card)
                cardLabel.setParent(None)  # Immediately remove the button from its parent
                cardLabel.deleteLater()  # Schedule it for deletion

        if pickUp:
            topCard = self.pile[-1]
            pixmap = QPixmap(fr"_internal/palaceData/cards/{topCard[0].lower()}_of_{topCard[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.view.pileLabel.setPixmap(pixmap)
            QCoreApplication.processEvents()
            time.sleep(1.5)
            self.pickUpPile()
            print(AIPlayer.hand)
            for card in reversed(AIPlayer.hand):
                if card[3]:
                    AIPlayer.bottomCards.append(AIPlayer.hand.pop(AIPlayer.hand.index(card)))
            self.view.updateAIHand(AIPlayer.hand)
            self.view.updateAIBottomCardButtons(AIPlayer.bottomCards)
            QCoreApplication.processEvents()
            self.view.placeButton.setText("Select A Card")
            return

        print(f"{AIPlayer.name} plays {', '.join([f'{card[0]} of {card[1]}' for card in playedCards])}")

        # Draw cards if fewer than 3 in hand
        while len(AIPlayer.hand) < 3 and self.deck:
            AIPlayer.hand.append(self.deck.pop(0))

        self.view.updateAIHand(AIPlayer.hand)

        # Check if 4 cards of the same rank in a row have been played
        if self.checkFourOfAKind():
            print("Four of a kind! Clearing the pile.")
            self.pile.clear()
            self.view.pileLabel.setText("Bombed")
            self.updateUI()
            gameOver = self.checkGameState()
            return

        if '2' in [card[0] for card in playedCards]:
            self.players[self.currentPlayerIndex].sevenSwitch = False
            if self.pile:
                topCard = self.pile[-1]
                pixmap = QPixmap(fr"_internal/palaceData/cards/{topCard[0].lower()}_of_{topCard[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.view.pileLabel.setPixmap(pixmap)
            else:
                self.view.pileLabel.setText("Pile: Empty")
            self.updateUI()
            gameOver = self.checkGameState()
            return
        elif '10' in [card[0] for card in playedCards]:
            self.pile.clear()
            self.players[self.currentPlayerIndex].sevenSwitch = False
            self.view.pileLabel.setText("Bombed")
            self.updateUI()
            gameOver = self.checkGameState()
            return
        else:
            if '7' in [card[0] for card in playedCards]:
                self.players[(self.currentPlayerIndex + 1) % len(self.players)].sevenSwitch = True
            else:
                self.players[(self.currentPlayerIndex + 1) % len(self.players)].sevenSwitch = False
            self.view.placeButton.setEnabled(False)
            topCard = self.pile[-1]
            pixmap = QPixmap(fr"_internal/palaceData/cards/{topCard[0].lower()}_of_{topCard[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.view.pileLabel.setPixmap(pixmap)
            self.updateUI()
            gameOver = self.checkGameState()
            if gameOver:
                return
            self.changeTurn()
        self.view.placeButton.setText("Select A Card")

    def changeTurn(self):
        self.currentPlayerIndex = (self.currentPlayerIndex + 1) % len(self.players)
        self.selectedCards = []  # Clear selected cards on turn change
        self.updateUI()

    def checkFourOfAKind(self):
        if len(self.pile) < 4:
            return False
        return len(set(card[0] for card in self.pile[-4:])) == 1

    def checkGameState(self):
        gameOver = False
        currentPlayer = self.players[self.currentPlayerIndex]
        if not currentPlayer.hand and not self.deck:
            if currentPlayer.topCards:
                currentPlayer.hand = currentPlayer.topCards
                currentPlayer.topCards = []
                print(currentPlayer.hand)
                if isinstance(currentPlayer, AIPlayer):
                    self.view.updateAIHand(currentPlayer.hand)
                    self.view.updateAITopCardButtons(currentPlayer.topCards)
                else:
                    self.view.updatePlayerHand(currentPlayer.hand)
                    self.view.updateTopCardButtons(currentPlayer.topCards)
            elif currentPlayer.bottomCards:
                currentPlayer.hand = currentPlayer.bottomCards
                currentPlayer.bottomCards = []
                if isinstance(currentPlayer, AIPlayer):
                    self.view.updateAIHand(currentPlayer.hand)
                    self.view.updateAIBottomCardButtons(self.players[1].bottomCards)
                else:
                    self.view.updatePlayerHand(currentPlayer.hand)
                    self.view.updateBottomCardButtons(currentPlayer.bottomCards)
            elif not currentPlayer.bottomCards:
                self.timer.stop()
                self.view.currentPlayerLabel.setText(f"{currentPlayer.name} wins!")
                self.view.pickUpPileButton.setDisabled(True)
                self.view.placeButton.setDisabled(True)
                for button in self.view.playCardButtons:
                    button.setDisabled(True)
                print(f"{currentPlayer.name} wins!")
                gameOver = True
        return gameOver

    def updatePlayableCards(self):
        currentPlayer = self.players[0]
        for i, lbl in enumerate(self.playCardButtons):
            handCard = currentPlayer.hand[i]
            if handCard[3] or self.isCardPlayable(handCard):  # Always enable bottom cards
                lbl.setEnabled(True)
            else:
                lbl.setEnabled(False)

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
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
