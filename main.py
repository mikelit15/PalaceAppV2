import sys
import random
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QLabel, QDialog, QGridLayout, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFontMetrics, QPixmap, QIcon, QTransform, QPainter
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
            controller = GameController(numPlayers, difficulty_level)  # Start game with selected number of players and difficulty level
            controller.view.show()

    def playOnline(self):
        onlineDialog = QDialog(self)
        onlineDialog.setWindowTitle("Online Multiplayer")
        onlineDialog.setGeometry(835, 400, 250, 150)
        onlineDialog.setWindowIcon(QIcon(r"_internal\palaceData\palace.ico"))
        layout = QVBoxLayout()
        rulesLabel = QLabel("Online Multiplayer COMING SOON!!!")
        rulesLabel.setTextFormat(Qt.TextFormat.RichText)
        rulesLabel.setWordWrap(True)
        layout.addWidget(rulesLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        closeButton = QPushButton("Close")
        closeButton.clicked.connect(onlineDialog.accept)
        layout.addWidget(closeButton)
        onlineDialog.setLayout(layout)
        onlineDialog.exec()
    
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
    def __init__(self, name, difficulty='medium'):
        super().__init__(name)
        self.difficulty = difficulty

    def playTurn(self, pile, deckSize, playerTopCards):
        if self.difficulty == 'easy':
            return self.playEasy(pile)
        elif self.difficulty == 'medium':
            return self.playMedium(pile, deckSize, playerTopCards)
        elif self.difficulty == 'hard':
            return self.playHard(pile, deckSize, playerTopCards)
        elif self.difficulty == 'impossible':
            return self.playImpossible(pile, deckSize, playerTopCards)
        
    def playEasy(self, pile):
        if not pile:
            return [min(self.hand, key=lambda card: VALUES[card[0]])]

        if all(card[3] for card in self.hand):
            return [random.choice(self.hand)]
        
        validCards = [card for card in self.hand if self.isCardPlayable(card, pile)]
        if not validCards:
            return -1

        return [min(validCards, key=lambda card: VALUES[card[0]])]

    def playMedium(self, pile, deckSize, playerTopCards):
        if not pile:
            return [min(self.hand, key=lambda card: VALUES[card[0]])]

        if all(card[3] for card in self.hand):
            return [random.choice(self.hand)]

        validCards = [card for card in self.hand if self.isCardPlayable(card, pile)]
        if not validCards:
            return -1

        nonSpecialCards = [card for card in validCards if card[0] not in ['2', '10']]
        if nonSpecialCards:
            validCards = nonSpecialCards

        validCards.sort(key=lambda card: VALUES[card[0]])

        if deckSize < 5 or len(playerTopCards) < 3:
            validCards.sort(key=lambda card: -VALUES[card[0]])

        sevens = [card for card in validCards if card[0] == '7']
        if sevens:
            return sevens

        return [validCards[0]]

    def playHard(self, pile, deckSize, playerTopCards):
        if not pile:
            return [min(self.hand, key=lambda card: VALUES[card[0]])]

        if all(card[3] for card in self.hand):
            return [random.choice(self.hand)]

        validCards = [card for card in self.hand if self.isCardPlayable(card, pile)]
        if not validCards:
            return -1

        nonSpecialCards = [card for card in validCards if card[0] not in ['2', '10']]
        if nonSpecialCards:
            validCards = nonSpecialCards

        validCards.sort(key=lambda card: VALUES[card[0]])

        if deckSize < 5 or len(playerTopCards) < 3:
            validCards.sort(key=lambda card: -VALUES[card[0]])

        sevens = [card for card in validCards if card[0] == '7' and all(VALUES[c[0]] > 7 for c in self.hand)]
        if sevens:
            return sevens

        if len(validCards) > 1 and validCards[0][0] == validCards[1][0]:
            return [card for card in validCards if card[0] == validCards[0][0]]

        return [validCards[0]]

    def playImpossible(self, pile, deckSize, playerTopCards):
        if not pile:
            return [min(self.hand, key=lambda card: VALUES[card[0]])]

        if all(card[3] for card in self.hand):
            return [random.choice(self.hand)]

        validCards = [card for card in self.hand if self.isCardPlayable(card, pile)]
        if not validCards:
            return -1

        validCards.sort(key=lambda card: VALUES[card[0]])

        validNonSpecialCards = [card for card in validCards if card[0] not in ['2', '10']]
        if validNonSpecialCards:
            highCards = [card for card in validNonSpecialCards if VALUES[card[0]] > VALUES[pile[-1][0]]]
            if highCards:
                return [highCards[0]]

        lowNonSpecialCards = [card for card in validCards if card[0] not in ['2', '10']]
        if lowNonSpecialCards:
            return [lowNonSpecialCards[0]]

        return [validCards[0]]

    def isCardPlayable(self, card, pile):
        topCard = pile[-1] if pile else None
        if self.sevenSwitch:
            return VALUES[card[0]] <= 7 or card[0] in ['2', '10']
        if not topCard:
            return True
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
        self.setGeometry(250, 75, 1440, 900)
        self.setFixedSize(1440, 900)
        
        # self.background_label = QLabel(self)
        # self.background_pixmap = QPixmap(r"_internal\palaceData\background.png")
        # self.background_label.setPixmap(self.background_pixmap)
        # self.background_label.setGeometry(self.rect())
        # self.background_label.lower() 

        self.layout = QGridLayout()
        
        # Center
        self.deckLabel = QLabel()  # Initialize the deck label
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

        # Player (Bottom)
        self.playerHandLabel = QLabel("Player's Hand")
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
        
        # AI Player 1 (Top)
        self.AIPlayerLabel1 = QLabel("")
        self.AIPlayerLabel1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.AIHandLayout1 = QHBoxLayout()
        self.AITopCardsLayout1 = QHBoxLayout()
        self.AIBottomCardsLayout1 = QHBoxLayout()

        self.AI1Container = QVBoxLayout()
        self.AI1Container.addLayout(self.AIHandLayout1)
        self.AI1Container.addWidget(self.AIPlayerLabel1)
        self.AI1Container.addLayout(self.AITopCardsLayout1)
        self.AI1Container.addLayout(self.AIBottomCardsLayout1)
        
        self.layout.addLayout(self.AI1Container, 0, 4)

        # AI Player 2 (Left)
        self.AIPlayerLabel2 = QLabel("")
        self.AIPlayerLabel2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.AIPlayerLabel2.setFixedWidth(20)
        self.AIHandLayout2 = QVBoxLayout()
        self.AITopCardsLayout2 = QVBoxLayout()
        self.AIBottomCardsLayout2 = QVBoxLayout()

        self.AI2Container = QHBoxLayout()
        self.AI2Container.addLayout(self.AIHandLayout2)
        self.AI2Container.addWidget(self.AIPlayerLabel2)
        self.AI2Container.addLayout(self.AITopCardsLayout2)
        self.AI2Container.addLayout(self.AIBottomCardsLayout2)

        self.layout.addLayout(self.AI2Container, 4, 0)

        # AI Player 3 (Right)
        self.AIPlayerLabel3 = QLabel("")
        self.AIPlayerLabel3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.AIHandLayout3 = QVBoxLayout()
        self.AITopCardsLayout3 = QVBoxLayout()
        self.AIBottomCardsLayout3 = QVBoxLayout()

        self.AI3Container = QHBoxLayout()
        self.AI3Container.addLayout(self.AIBottomCardsLayout3)
        self.AI3Container.addLayout(self.AITopCardsLayout3)
        self.AI3Container.addWidget(self.AIPlayerLabel3)
        self.AI3Container.addLayout(self.AIHandLayout3)

        self.layout.addLayout(self.AI3Container, 4, 8)

        # Hide AI Player 2 and 3 layouts if less than 3 or 4 players    
        if self.controller.numPlayers < 3:
            self.AIPlayerLabel2.setText("")
            self.setGeometry(550, 75, 900, 900)
            self.setFixedSize(900, 900)
        if self.controller.numPlayers < 4:
            self.AIPlayerLabel3.setText("")

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
    
    def updateHand(self, hand, layout, isPlayer=True, rotate=False):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if isPlayer:
            self.controller.playCardButtons = []

        for idx, card in enumerate(hand):
            button = QLabel()
            if rotate:
                button.setFixedSize(BUTTON_HEIGHT, BUTTON_WIDTH)
            else:
                button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            if not card[3]:  # Check if isBottomCard is False
                pixmap = QPixmap(
                    fr"_internal\palaceData\cards\{card[0].lower()}_of_{card[1].lower()}.png")
                if rotate:
                    transform = QTransform().rotate(90)
                    pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation).scaled(CARD_HEIGHT, CARD_WIDTH, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                else:
                    pixmap = pixmap.scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                button.setPixmap(pixmap)
            else:
                pixmap = QPixmap(r"_internal\palaceData\cards\back.png")
                if rotate:
                    transform = QTransform().rotate(90)
                    pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation).scaled(CARD_HEIGHT, CARD_WIDTH, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                else:
                    pixmap = pixmap.scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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

    def updateAIHand(self, hand, ai_index):
        rotate = ai_index in [2, 3]  # Rotate cards for AI2 and AI3
        layout = getattr(self, f'AIHandLayout{ai_index}')
        self.updateHand(hand, layout, isPlayer=False, rotate=rotate)

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
        if not topCards:
            self.placeholder = QLabel()
            self.placeholder.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            self.topCardsLayout.addWidget(self.placeholder)
        else:
            # Remove the placeholder if it exists
            for i in reversed(range(self.topCardsLayout.count())):
                widget = self.topCardsLayout.itemAt(i).widget()
                if isinstance(widget, QLabel) and not widget.pixmap():
                    widget.deleteLater()
        
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
        if not bottomCards:
            self.placeholder = QLabel()
            self.placeholder.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            self.bottomCardsLayout.addWidget(self.placeholder)
        else:
            # Remove the placeholder if it exists
            for i in reversed(range(self.topCardsLayout.count())):
                widget = self.bottomCardsLayout.itemAt(i).widget()
                if isinstance(widget, QLabel) and not widget.pixmap():
                    widget.deleteLater()

    def updateAITopCardButtons(self, topCards, ai_index):
        layout = getattr(self, f'AITopCardsLayout{ai_index}')
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

        for card in topCards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(f"_internal/palaceData/cards/{card[0].lower()}_of_{card[1].lower()}.png")
            if ai_index in [2, 3]:  # Rotate cards for AI2 and AI3
                transform = QTransform().rotate(90 if ai_index == 2 else -90)
                pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation).scaled(CARD_HEIGHT, CARD_WIDTH, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                button.setFixedSize(BUTTON_HEIGHT, BUTTON_WIDTH)
                button.setPixmap(pixmap)
                button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                pixmap = pixmap.scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                button.setPixmap(pixmap)
                button.setDisabled(True)
                button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(button)
        if not topCards:
            if ai_index in [2, 3]:
                self.placeholder = QLabel()
                self.placeholder.setFixedSize(BUTTON_HEIGHT, BUTTON_WIDTH)
                layout.addWidget(self.placeholder)
            else:
                self.placeholder = QLabel()
                self.placeholder.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
                layout.addWidget(self.placeholder)
        else:
            # Remove the placeholder if it exists
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QLabel) and not widget.pixmap():
                    widget.deleteLater()

    def updateAIBottomCardButtons(self, bottomCards, ai_index):
        layout = getattr(self, f'AIBottomCardsLayout{ai_index}')
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

        for card in bottomCards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(r"_internal\palaceData\cards\back.png")
            if ai_index in [2, 3]:  # Rotate cards for AI2 and AI3
                transform = QTransform().rotate(90 if ai_index == 2 else -90)
                pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation).scaled(CARD_HEIGHT, CARD_WIDTH, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                button.setFixedSize(BUTTON_HEIGHT, BUTTON_WIDTH)
                button.setPixmap(pixmap)
                button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                pixmap = pixmap.scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                button.setPixmap(pixmap)
                button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(button)
        if not bottomCards:
            if ai_index in [2, 3]:
                self.placeholder = QLabel()
                self.placeholder.setFixedSize(BUTTON_HEIGHT, BUTTON_WIDTH)
                layout.addWidget(self.placeholder)
            else:
                self.placeholder = QLabel()
                self.placeholder.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
                layout.addWidget(self.placeholder)
        else:
            # Remove the placeholder if it exists
            for i in reversed(range(self.topCardsLayout.count())):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QLabel) and not widget.pixmap():
                    widget.deleteLater()

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
        self.currentPlayerLabel.setText("Current Player: ")
        self.pileLabel.setText("Pile: Empty")
        self.pileLabel.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.controller.startGameLoop()  # Start the game loop after top card selection
        for index, _ in enumerate(self.controller.players[1:], start=1):
            self.updateAIHand(self.controller.players[index].hand, index)
            if index == 1:
                self.AIPlayerLabel1.setText("AI Player 1's Hand")
            elif index == 2:
                self.AIPlayerLabel2.setText("AI Player 2's Hand")
                font = self.currentPlayerLabel.font()
                font.setPointSize(9)  
                self.AIPlayerLabel2.setFont(font)
                font_metrics = QFontMetrics(font)
                text_height = font_metrics.height()
                self.AIPlayerLabel2.setFixedHeight(190)
                self.AIPlayerLabel2.setFixedWidth(25)
                transform = QTransform().rotate(90)
                pixmap = QPixmap(self.AIPlayerLabel2.size())
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
                painter.setFont(font)
                painter.setPen(Qt.GlobalColor.white)
                painter.translate(pixmap.width(), 0)
                painter.rotate(90)
                painter.drawText(0, 0, self.AIPlayerLabel2.height(), self.AIPlayerLabel2.width(), Qt.AlignmentFlag.AlignCenter, self.AIPlayerLabel2.text())
                painter.end()
                self.AIPlayerLabel2.setPixmap(pixmap)
            elif index == 3:
                self.AIPlayerLabel3.setText("AI Player 3's Hand") 
                # Rotate the text
                font = self.currentPlayerLabel.font()
                font.setPointSize(9) 
                self.AIPlayerLabel3.setFont(font)
                font_metrics = QFontMetrics(font)
                text_height = font_metrics.height()
                self.AIPlayerLabel3.setFixedHeight(190)
                self.AIPlayerLabel3.setFixedWidth(25)
                transform = QTransform().rotate(-90)
                pixmap = QPixmap(self.AIPlayerLabel3.size())
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
                painter.setFont(font)
                painter.setPen(Qt.GlobalColor.white)
                painter.translate(0, pixmap.height())
                painter.rotate(-90)
                painter.drawText(0, 0, self.AIPlayerLabel3.height(), self.AIPlayerLabel3.width(), Qt.AlignmentFlag.AlignCenter, self.AIPlayerLabel3.text())
                painter.end()
                self.AIPlayerLabel3.setPixmap(pixmap)

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
    def __init__(self, numPlayers, difficulty):
        self.numPlayers = numPlayers
        self.difficulty = difficulty
        self.view = GameView(self)
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
                ai_index = self.players.index(currentPlayer)
                self.view.updateAITopCardButtons(currentPlayer.topCards, ai_index)
            else:
                self.view.updateTopCardButtons(currentPlayer.topCards)

        # self.view.setPlayerHandEnabled(False)
        self.view.placeButton.setText("AI Turn...")
        self.updateUI()
        self.changeTurn()
        
    def setupGame(self):
        self.players.append(Player("Player"))
        for _ in range(self.numPlayers - 1):
            self.players.append(AIPlayer(f"AI{_}", self.difficulty))
        self.deck = self.createDeck()
        random.shuffle(self.deck)
        self.dealInitialCards()
        self.view.updatePlayerHand(self.players[0].hand)
        self.view.showTopCardSelection(self.players[0])

    def proceedWithGameSetup(self):
        for index, AIPlayer in enumerate(self.players[1:], start=1):
            AIPlayer.chooseTopCards()
            self.view.updateAITopCardButtons(AIPlayer.topCards, index)
            self.view.updateAIBottomCardButtons(AIPlayer.bottomCards, index)
        self.view.updateBottomCardButtons(self.players[0].bottomCards)
        self.topCardSelectionPhase = False
        self.updateUI()
        self.startGameLoop()

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
                ai_index = self.players.index(currentPlayer)
                self.view.updateAIHand(currentPlayer.hand, ai_index)
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
        time.sleep(0.7)
        AIPlayer = self.players[self.currentPlayerIndex]
        ai_index = self.players.index(AIPlayer)  # Get the index of the current AI player
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
            ai_hand_layout = getattr(self.view, f'AIHandLayout{ai_index}')
            cardLabel = ai_hand_layout.itemAt(cardIndex).widget()
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
            for card in reversed(AIPlayer.hand):
                if card[3]:
                    AIPlayer.bottomCards.append(AIPlayer.hand.pop(AIPlayer.hand.index(card)))
            self.view.updateAIHand(AIPlayer.hand, ai_index)
            self.view.updateAIBottomCardButtons(AIPlayer.bottomCards, ai_index)
            # QCoreApplication.processEvents()
            self.view.placeButton.setText("Select A Card")
            return

        print(f"{AIPlayer.name} plays {', '.join([f'{card[0]} of {card[1]}' for card in playedCards])}")

        while len(AIPlayer.hand) < 3 and self.deck:
            AIPlayer.hand.append(self.deck.pop(0))

        self.view.updateAIHand(AIPlayer.hand, ai_index)

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
                if isinstance(currentPlayer, AIPlayer):
                    ai_index = self.players.index(currentPlayer)
                    self.view.updateAIHand(currentPlayer.hand, ai_index)
                    self.view.updateAITopCardButtons(currentPlayer.topCards, ai_index)
                else:
                    self.view.updatePlayerHand(currentPlayer.hand)
                    self.view.updateTopCardButtons(currentPlayer.topCards)
            elif currentPlayer.bottomCards:
                currentPlayer.hand = currentPlayer.bottomCards
                currentPlayer.bottomCards = []
                if isinstance(currentPlayer, AIPlayer):
                    ai_index = self.players.index(currentPlayer)
                    self.view.updateAIHand(currentPlayer.hand, ai_index)
                    self.view.updateAIBottomCardButtons(currentPlayer.bottomCards, ai_index)
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
