import random
import time
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QCoreApplication, QTimer
from View import View
from Player import Player
from AIPlayer import AIPlayer

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
CARD_WIDTH = 56
CARD_HEIGHT = 84
BUTTON_WIDTH = 66
BUTTON_HEIGHT = 87

class Controller:
    '''
    Initializes the Controller class, sets up the game state, and starts 
    the game loop.

    @param self - The instance of the Controller class
    @param numPlayers (int) - The number of players in the game
    @param difficulty (str) - The difficulty level of the AI players

    @return None

    @author Mike
    '''
    def __init__(self, numPlayers, difficulty):
        self.numPlayers = numPlayers
        self.difficulty = difficulty
        self.view = View(self)
        self.players = []
        self.deck = []
        self.pile = []
        self.currentPlayerIndex = 0
        self.selectedCards = [] 
        self.playCardButtons = []  
        self.topCardSelectionPhase = True  
        self.setupGame()

    '''
    Starts the game loop with a timer to manage turns and game state updates.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
    def startGameLoop(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.gameLoop)
        self.timer.start(1000)  

    '''
    The main game loop that handles the current player's turn and updates the 
    game state.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
    def gameLoop(self):
        currentPlayer = self.players[self.currentPlayerIndex]
        if isinstance(currentPlayer, AIPlayer):
            self.AIPlayTurn()
        else:
            self.view.updateUI(currentPlayer, len(self.deck), self.pile)

    '''
    Handles the logic for a player picking up the pile of cards.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
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

        for card in pickedUpCards:
            if card[3]: 
                if card in currentPlayer.hand:
                    index = currentPlayer.hand.index(card)
                    currentPlayer.hand[index] = (card[0], card[1], card[2], False)  
                    if index < self.view.playerHandLayout.count():
                        self.view.revealCard(self.view.playerHandLayout.itemAt(index).widget(), card) 

        for card in reversed(currentPlayer.hand):
            if card[2]:
                currentPlayer.topCards.append(currentPlayer.hand.pop(currentPlayer.hand.index(card)))
                top = True
        if top:
            if isinstance(currentPlayer, AIPlayer):
                AI_Index = self.players.index(currentPlayer)
                self.view.updateAITopCardButtons(currentPlayer.topCards, AI_Index)
            else:
                self.view.updateTopCardButtons(currentPlayer.topCards)

        # self.view.setPlayerHandEnabled(False)
        self.view.placeButton.setText("AI Turn...")
        self.updateUI()
        self.changeTurn()
    
    '''
    Sets up the game by creating players, shuffling the deck, and dealing 
    initial cards.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
    def setupGame(self):
        self.players.append(Player("Player"))
        for _ in range(self.numPlayers - 1):
            self.players.append(AIPlayer(f"AI{_}", self.difficulty))
        self.deck = self.createDeck()
        random.shuffle(self.deck)
        self.dealInitialCards()
        self.view.updatePlayerHand(self.players[0].hand)
        self.view.showTopCardSelection(self.players[0])

    '''
    Proceeds with the game setup after the top cards have been selected by 
    the players.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
    def proceedWithGameSetup(self):
        for index, AIPlayer in enumerate(self.players[1:], start=1):
            AIPlayer.chooseTopCards()
            self.view.updateAITopCardButtons(AIPlayer.topCards, index)
            self.view.updateAIBottomCardButtons(AIPlayer.bottomCards, index)
        self.view.updateBottomCardButtons(self.players[0].bottomCards)
        self.topCardSelectionPhase = False
        self.updateUI()
        self.startGameLoop()

    '''
    Creates a standard deck of cards.

    @param self - The instance of the Controller class

    @return deck (list) - The created deck of cards

    @author Mike
    '''
    def createDeck(self):
        suits = ['diamonds', 'hearts', 'clubs', 'spades']
        return [(rank, suit, False, False) for rank in RANKS for suit in suits] 

    '''
    Deals the initial cards to all players.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
    def dealInitialCards(self):
        for player in self.players:
            player.bottomCards = [(card[0], card[1], False, True) for card in self.deck[:3]]
            player.hand = self.deck[3:9]
            self.deck = self.deck[9:]

    '''
    Updates the UI elements to reflect the current game state.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
    def updateUI(self):
        currentPlayer = self.players[self.currentPlayerIndex]
        if not self.topCardSelectionPhase:
            self.view.updateUI(currentPlayer, len(self.deck), self.pile)
            if isinstance(currentPlayer, AIPlayer):
                self.view.placeButton.setText("AI Turn...")
                AI_Index = self.players.index(currentPlayer)
                self.view.updateAIHand(currentPlayer.hand, AI_Index)
                self.view.pickUpPileButton.setDisabled(True)
            else:
                self.view.placeButton.setText("Select A Card")
                self.view.pickUpPileButton.setDisabled(False)
                self.view.updatePlayerHand(currentPlayer.hand)
                if not self.topCardSelectionPhase:
                    self.updatePlayableCards()

    '''
    Prepares a card for placement by selecting or deselecting it and updating 
    the UI accordingly.

    @param self - The instance of the Controller class
    @param cardIndex (int) - The index of the card to prepare for placement
    @param cardLabel (QLabel) - The label corresponding to the card

    @return None

    @author Mike
    '''
    def prepareCardPlacement(self, cardIndex, cardLabel):
        card = self.players[self.currentPlayerIndex].hand[cardIndex]
        if (card, cardLabel) in self.selectedCards:
            self.selectedCards.remove((card, cardLabel))
            cardLabel.setStyleSheet("border: 0px solid black; background-color: transparent;") 
        else:
            self.selectedCards.append((card, cardLabel))
            cardLabel.setStyleSheet("border: 0px solid black; background-color: blue;") 
        
        # Enable all buttons with the same rank, disable the rest
        selectedCardRank = card[0]
        if not self.selectedCards:
            for i, lbl in enumerate(self.playCardButtons):
                handCard = self.players[self.currentPlayerIndex].hand[i]
                if handCard[3] or self.isCardPlayable(handCard):  
                    lbl.setEnabled(True)
        else:
            for i, lbl in enumerate(self.playCardButtons):
                handCard = self.players[self.currentPlayerIndex].hand[i]
                if handCard[0] == selectedCardRank or (handCard, lbl) in self.selectedCards:
                    lbl.setEnabled(True)
                elif not handCard[3]:  
                    lbl.setEnabled(False)
        self.view.placeButton.setEnabled(len(self.selectedCards) > 0)  
        if self.view.placeButton.text() == "Place":
            self.view.placeButton.setText("Select A Card")
        else:
            self.view.placeButton.setText("Place")
    
    '''
    Checks if a card is playable based on the top card of the pile and the 
    sevenSwitch flag.

    @param self - The instance of the Controller class
    @param card (tuple) - The card to check

    @return (bool) - True if the card is playable, False otherwise

    @author Mike
    '''
    def isCardPlayable(self, card):
        topCard = self.pile[-1] if self.pile else None
        if self.players[self.currentPlayerIndex].sevenSwitch:
            return VALUES[card[0]] <= 7 or card[0] in ['2', '10']
        if not topCard:
            return True 
        return card[0] == '2' or card[0] == '10' or VALUES[card[0]] >= VALUES[topCard[0]]
    
    '''
    Places the selected cards onto the pile and handles the game logic for 
    the current player's turn.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
    def placeCard(self):
        player = self.players[self.currentPlayerIndex]
        playedCards = []
        pickUp = False

        for card, button in sorted(self.selectedCards, key=lambda x: player.hand.index(x[0])):
            if card[3] and not self.isCardPlayable(card):
                playedCards.append(card)
                for i, card in enumerate(playedCards):
                    self.pile.append(player.hand.pop(player.hand.index(playedCards[i])))
                    self.pile[-1] = (card[0], card[1], card[2], False)
                    self.view.revealCard(button, card)
                pickUp = True
                button.setParent(None) 
                button.deleteLater() 
            else:
                playedCards.append(card)
                for i, card in enumerate(playedCards):
                    if card[3]: 
                        playedCards[i] = (card[0], card[1], card[2], False) 
                player.playCard(player.hand.index(card), self.pile)
                self.view.revealCard(button, card)
                button.setParent(None)
                button.deleteLater()  
                
        if pickUp:
            topCard = self.pile[-1]
            pixmap = QPixmap(fr"_internal/palaceData/cards/{topCard[0].lower()}_of_{topCard[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.view.pileLabel.setPixmap(pixmap)
            QCoreApplication.processEvents()
            time.sleep(1)      
            self.pickUpPile()
            for card in reversed(player.hand):
                if card[3]:
                    player.bottomCards.append(player.hand.pop(player.hand.index(card)))
            self.view.updatePlayerHand(player.hand)
            self.view.updateBottomCardButtons(player.bottomCards)
            self.view.setPlayerHandEnabled(False)
            self.view.placeButton.setText("AI Turn...")
            return

        self.selectedCards = []
        print(f"{player.name} plays {', '.join([f'{card[0]} of {card[1]}' for card in playedCards])}")

        # Draw cards if fewer than 3 in hand
        while len(player.hand) < 3 and self.deck:
            player.hand.append(self.deck.pop(0))

        self.view.updatePlayerHand(player.hand) 

        self.updatePlayableCards()

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
            self.view.placeButton.setText("Opponent's Turn...")
            
    '''
    Handles the AI player's turn, determining and executing the best move 
    based on the difficulty level and game state.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
    def AIPlayTurn(self):
        time.sleep(1)
        AIPlayer = self.players[self.currentPlayerIndex]
        AI_Index = self.players.index(AIPlayer)
        playerTopCards = self.players[0].topCards
        playerHand = self.players[0].hand
        playerBottomCards = self.players[0].bottomCards
        playedCards = []
        pickUp = False

        if self.difficulty == 'impossible':
            cardsToPlay = AIPlayer.playTurn(self.pile, len(self.deck), playerTopCards, playerHand, playerBottomCards)
        else:
            cardsToPlay = AIPlayer.playTurn(self.pile, len(self.deck), playerTopCards)

        if cardsToPlay == -1:
            self.pickUpPile()
            time.sleep(1)
            return

        for card in cardsToPlay:
            cardIndex = AIPlayer.hand.index(card)
            AI_HandLayout = getattr(self.view, f'AIHandLayout{AI_Index}')
            cardLabel = AI_HandLayout.itemAt(cardIndex).widget()
            if card[3] and not self.isCardPlayable(card):
                playedCards.append(card)
                for i, card in enumerate(playedCards):
                    self.pile.append(AIPlayer.hand.pop(AIPlayer.hand.index(playedCards[i])))
                    self.pile[-1] = (card[0], card[1], card[2], False)
                    self.view.revealCard(cardLabel, card)
                pickUp = True
                cardLabel.setParent(None)
                cardLabel.deleteLater()
            else:
                playedCards.append(card)
                self.pile.append(AIPlayer.hand.pop(AIPlayer.hand.index(card)))
                self.pile[-1] = (card[0], card[1], False, False)
                self.view.revealCard(cardLabel, card)
                cardLabel.setParent(None)
                cardLabel.deleteLater()

        if pickUp:
            topCard = self.pile[-1]
            pixmap = QPixmap(fr"_internal/palaceData/cards/{topCard[0].lower()}_of_{topCard[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.view.pileLabel.setPixmap(pixmap)
            self.pickUpPile()
            for card in reversed(AIPlayer.hand):
                if card[3]:
                    AIPlayer.bottomCards.append(AIPlayer.hand.pop(AIPlayer.hand.index(card)))
            self.view.updateAIHand(AIPlayer.hand, AI_Index)
            self.view.updateAIBottomCardButtons(AIPlayer.bottomCards, AI_Index)
            time.sleep(1)
            return

        print(f"{AIPlayer.name} plays {', '.join([f'{card[0]} of {card[1]}' for card in playedCards])}")

        while len(AIPlayer.hand) < 3 and self.deck:
            AIPlayer.hand.append(self.deck.pop(0))

        self.view.updateAIHand(AIPlayer.hand, AI_Index)

        if self.checkFourOfAKind():
            print("Four of a kind! Clearing the pile.")
            self.pile.clear()
            self.view.pileLabel.setText("Bombed")
            self.updateUI()
            gameOver = self.checkGameState()
            time.sleep(1)
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
            time.sleep(1)
            return
        elif '10' in [card[0] for card in playedCards]:
            self.pile.clear()
            self.players[self.currentPlayerIndex].sevenSwitch = False
            self.view.pileLabel.setText("Bombed")
            self.updateUI()
            gameOver = self.checkGameState()
            time.sleep(1)
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

    '''
    Changes the turn to the next player and updates the game state.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
    def changeTurn(self):
        self.currentPlayerIndex = (self.currentPlayerIndex + 1) % len(self.players)
        if self.currentPlayerIndex == 0:
            self.view.placeButton.setText("Select A Card")
        self.selectedCards = [] 
        self.updateUI()

    '''
    Checks if the top four cards in the pile are of the same rank, indicating 
    a bomb.

    @param self - The instance of the Controller class

    @return (bool) - True if the top four cards are of the same rank, False otherwise

    @author Mike
    '''
    def checkFourOfAKind(self):
        if len(self.pile) < 4:
            return False
        return len(set(card[0] for card in self.pile[-4:])) == 1

    '''
    Checks the game state to determine if a player has won or if the game 
    should continue.

    @param self - The instance of the Controller class

    @return (bool) - True if the game is over, False otherwise

    @author Mike
    '''
    def checkGameState(self):
        gameOver = False
        currentPlayer = self.players[self.currentPlayerIndex]
        if not currentPlayer.hand and not self.deck:
            if currentPlayer.topCards:
                currentPlayer.hand = currentPlayer.topCards
                currentPlayer.topCards = []
                if isinstance(currentPlayer, AIPlayer):
                    AI_Index = self.players.index(currentPlayer)
                    self.view.updateAIHand(currentPlayer.hand, AI_Index)
                    self.view.updateAITopCardButtons(currentPlayer.topCards, AI_Index)
                else:
                    self.view.updatePlayerHand(currentPlayer.hand)
                    self.view.updateTopCardButtons(currentPlayer.topCards)
            elif currentPlayer.bottomCards:
                currentPlayer.hand = currentPlayer.bottomCards
                currentPlayer.bottomCards = []
                if isinstance(currentPlayer, AIPlayer):
                    AI_Index = self.players.index(currentPlayer)
                    self.view.updateAIHand(currentPlayer.hand, AI_Index)
                    self.view.updateAIBottomCardButtons(currentPlayer.bottomCards, AI_Index)
                else:
                    self.view.updatePlayerHand(currentPlayer.hand)
                    self.view.updateBottomCardButtons(currentPlayer.bottomCards)
            elif not currentPlayer.bottomCards:
                placeholder = QLabel()
                placeholder.setFixedSize(BUTTON_HEIGHT, BUTTON_WIDTH)
                currentPlayer.hand.append(placeholder)
                self.timer.stop()
                self.view.currentPlayerLabel.setText(f"{currentPlayer.name} wins!")
                self.view.pickUpPileButton.setDisabled(True)
                self.view.placeButton.setDisabled(True)
                for button in self.playCardButtons:
                    button.setDisabled(True)
                print(f"{currentPlayer.name} wins!")
                gameOver = True
        return gameOver
    
    '''
    Updates the playable cards for the current player based on the top card 
    of the pile and the sevenSwitch flag.

    @param self - The instance of the Controller class

    @return None

    @author Mike
    '''
    def updatePlayableCards(self):
        currentPlayer = self.players[0]
        for i, lbl in enumerate(self.playCardButtons):
            handCard = currentPlayer.hand[i]
            if handCard[3] or self.isCardPlayable(handCard):
                lbl.setEnabled(True)
            else:
                lbl.setEnabled(False)