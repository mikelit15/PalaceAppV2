from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QLabel, QGridLayout, QSpacerItem, QSizePolicy
from PySide6.QtGui import QFontMetrics, QPixmap, QIcon, QTransform, QPainter
from PySide6.QtCore import Qt

CARD_WIDTH = 56
CARD_HEIGHT = 84
BUTTON_WIDTH = 66
BUTTON_HEIGHT = 87

class View(QWidget):
    global scalingFactorWidth
    global scalingFactorHeight

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.initUI()

    '''
    Initializes the UI for the View, sets up the layout, and connects the 
    necessary buttons to their functions.

    @param self - The instance of the View class

    @return None

    @author Mike
    '''
    def initUI(self):
        # Set up main window properties
        self.setWindowTitle('Palace Card Game')
        self.setWindowIcon(QIcon(r"_internal\palaceData\palace.ico"))
        self.setGeometry(410, 75, 1095, 900)
        self.setFixedSize(1095, 900)
        
        # self.backgroundLabel = QLabel(self)
        # self.backgroundPixmap = QPixmap(r"_internal\palaceData\background.png")
        # self.backgroundLabel.setPixmap(self.backgroundPixmap)
        # self.backgroundLabel.setGeometry(self.rect())
        # self.backgroundLabel.lower()
        
        self.layout = QGridLayout()
        
        # Center layout setup
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

        # Player (Bottom) layout setup
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
        
        # AI Player 1 (Top) layout setup
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

        # AI Player 2 (Left) layout setup
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

        # AI Player 3 (Right) layout setup
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
            self.setGeometry(550, 75, 900, 850)
            self.setFixedSize(900, 850)
        if self.controller.numPlayers < 4:
            self.AIPlayerLabel3.setText("")

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
    
    '''
    Updates the displayed hand of a player or AI in the game UI.

    @param self - The instance of the View class
    @param hand (list) - The list of cards in the hand
    @param layout (QLayout) - The layout to update with the hand cards
    @param isPlayer (bool) - Flag to indicate if the hand belongs to the player
    @param rotate (bool) - Flag to indicate if the cards should be rotated

    @return None

    @author Mike
    '''
    def updateHand(self, hand, layout, isPlayer=True, rotate=False):
        # Clear the existing layout
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
            if not card[3] and isPlayer: 
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

    '''
    Updates the displayed hand of the player in the game UI.

    @param self - The instance of the View class
    @param hand (list) - The list of cards in the player's hand

    @return None

    @author Mike
    '''
    def updatePlayerHand(self, hand):
        self.updateHand(hand, self.playerHandLayout, isPlayer=True)

    '''
    Updates the displayed hand of an AI player in the game UI.

    @param self - The instance of the View class
    @param hand (list) - The list of cards in the AI player's hand
    @param AI_Index (int) - The index of the AI player

    @return None

    @author Mike
    '''
    def updateAIHand(self, hand, AI_Index):
        rotate = AI_Index in [2, 3]  # Rotate cards for AI2 and AI3
        layout = getattr(self, f'AIHandLayout{AI_Index}')
        self.updateHand(hand, layout, isPlayer=False, rotate=rotate)

    '''
    Updates the displayed top cards of the player in the game UI.

    @param self - The instance of the View class
    @param topCards (list) - The list of top cards

    @return None

    @author Mike
    '''
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
            for i in reversed(range(self.topCardsLayout.count())):
                widget = self.topCardsLayout.itemAt(i).widget()
                if isinstance(widget, QLabel) and not widget.pixmap():
                    widget.deleteLater()
    
    '''
    Updates the displayed bottom cards of the player in the game UI.

    @param self - The instance of the View class
    @param bottomCards (list) - The list of bottom cards

    @return None

    @author Mike
    '''
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
            for i in reversed(range(self.topCardsLayout.count())):
                widget = self.bottomCardsLayout.itemAt(i).widget()
                if isinstance(widget, QLabel) and not widget.pixmap():
                    widget.deleteLater()

    '''
    Updates the displayed top cards of an AI player in the game UI.

    @param self - The instance of the View class
    @param topCards (list) - The list of top cards
    @param AI_Index (int) - The index of the AI player

    @return None

    @author Mike
    '''
    def updateAITopCardButtons(self, topCards, AI_Index):
        layout = getattr(self, f'AITopCardsLayout{AI_Index}')
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

        for card in topCards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(f"_internal/palaceData/cards/{card[0].lower()}_of_{card[1].lower()}.png")
            if AI_Index in [2, 3]:  # Rotate cards for AI2 and AI3
                transform = QTransform().rotate(90 if AI_Index == 2 else -90)
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
            if AI_Index in [2, 3]: # Rotate cards for AI2 and AI3
                self.placeholder = QLabel()
                self.placeholder.setFixedSize(BUTTON_HEIGHT, BUTTON_WIDTH)
                layout.addWidget(self.placeholder)
            else:
                self.placeholder = QLabel()
                self.placeholder.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
                layout.addWidget(self.placeholder)
        else:
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QLabel) and not widget.pixmap():
                    widget.deleteLater()

    '''
    Updates the displayed bottom cards of an AI player in the game UI.

    @param self - The instance of the View class
    @param bottomCards (list) - The list of bottom cards
    @param AI_Index (int) - The index of the AI player

    @return None

    @author Mike
    '''
    def updateAIBottomCardButtons(self, bottomCards, AI_Index):
        layout = getattr(self, f'AIBottomCardsLayout{AI_Index}')
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

        for card in bottomCards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(r"_internal\palaceData\cards\back.png")
            if AI_Index in [2, 3]:  # Rotate cards for AI2 and AI3
                transform = QTransform().rotate(90 if AI_Index == 2 else -90)
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
            if AI_Index in [2, 3]: # Rotate cards for AI2 and AI3
                self.placeholder = QLabel()
                self.placeholder.setFixedSize(BUTTON_HEIGHT, BUTTON_WIDTH)
                layout.addWidget(self.placeholder)
            else:
                self.placeholder = QLabel()
                self.placeholder.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
                layout.addWidget(self.placeholder)
        else:
            for i in reversed(range(self.topCardsLayout.count())):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QLabel) and not widget.pixmap():
                    widget.deleteLater()

    '''
    Updates the UI elements to reflect the current game state.

    @param self - The instance of the View class
    @param currentPlayer (Player) - The current player
    @param deckSize (int) - The number of cards remaining in the deck
    @param pile (list) - The current pile of cards

    @return None

    @author Mike
    '''
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

    '''
    Reveals a card by updating its label with the card's image.

    @param self - The instance of the View class
    @param cardLabel (QLabel) - The label to update with the card's image
    @param card (tuple) - The card to reveal

    @return None

    @author Mike
    '''
    def revealCard(self, cardLabel, card):
        pixmap = QPixmap(fr"_internal/palaceData/cards/{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        cardLabel.setPixmap(pixmap)

    '''
    Displays the top card selection phase for the player.

    @param self - The instance of the View class
    @param player (Player) - The player selecting top cards

    @return None

    @author Mike
    '''
    def showTopCardSelection(self, player):
        self.chosenCards = []
        self.cardButtons = []

    '''
    Selects or deselects a top card for the player during the selection phase.

    @param self - The instance of the View class
    @param cardIndex (int) - The index of the card to select or deselect
    @param button (QLabel) - The button corresponding to the card

    @return None

    @author Mike
    '''
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

    '''
    Confirms the selection of the top cards for the player and proceeds with 
    the game setup.

    @param self - The instance of the View class

    @return None

    @author Mike
    '''
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
        self.controller.startGameLoop()  
        for index, _ in enumerate(self.controller.players[1:], start=1):
            self.updateAIHand(self.controller.players[index].hand, index)
            if index == 1:
                self.AIPlayerLabel1.setText("AI Player 1's Hand")
            elif index == 2:
                self.AIPlayerLabel2.setText("AI Player 2's Hand")
                font = self.currentPlayerLabel.font()
                font.setPointSize(9)  
                self.AIPlayerLabel2.setFont(font)
                fontMetrics = QFontMetrics(font)
                textHeight = fontMetrics.height()
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
                fontMetrics = QFontMetrics(font)
                textHeight = fontMetrics.height()
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
    
    '''
    Clears the selection layout for the top card selection phase.

    @param self - The instance of the View class

    @return None

    @author Mike
    '''
    def clearSelectionLayout(self):
        self.chosenCards = []
        self.cardButtons = []
    
    '''
    Enables or disables the player's hand buttons.

    @param self - The instance of the View class
    @param enabled (bool) - Flag to enable or disable the buttons

    @return None

    @author Mike
    '''
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