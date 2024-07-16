from Player import Player
import random

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

class AIPlayer(Player):
    '''
    Initializes the AIPlayer class, sets up the difficulty level, and inherits 
    from the Player class.

    @param self - The instance of the AIPlayer class
    @param name (str) - The name of the AI player
    @param difficulty (str) - The difficulty level of the AI player

    @return None

    @author Mike
    '''
    def __init__(self, name, difficulty='medium'):
        super().__init__(name)
        self.difficulty = difficulty

    '''
    Determines the AI player's move based on the difficulty level and the 
    state of the game.

    @param self - The instance of the AIPlayer class
    @param pile (list) - The pile to play cards onto
    @param deckSize (int) - The number of cards remaining in the deck
    @param playerTopCards (list) - The top cards of the player

    @return (list) - The cards to play or -1 if the AI should pick up the pile

    @author Mike
    '''
    def playTurn(self, pile, deckSize, playerTopCards):
        if self.difficulty == 'easy':
            return self.playEasy(pile)
        elif self.difficulty == 'medium':
            return self.playMedium(pile, deckSize, playerTopCards)
        elif self.difficulty == 'hard':
            return self.playHard(pile, deckSize, playerTopCards)
        elif self.difficulty == 'impossible':
            return self.playImpossible(pile, deckSize, playerTopCards)
    
    '''
    Determines the AI player's move in easy mode by playing the lowest ranked 
    valid card or picking up the pile if no valid cards are available.

    @param self - The instance of the AIPlayer class
    @param pile (list) - The pile to play cards onto

    @return (list) - The card to play or -1 if the AI should pick up the pile

    @author Mike
    '''
    def playEasy(self, pile):
        if not pile:
            return [min(self.hand, key=lambda card: VALUES[card[0]])]

        if all(card[3] for card in self.hand):
            return [random.choice(self.hand)]
        
        validCards = [card for card in self.hand if self.isCardPlayable(card, pile)]
        if not validCards:
            return -1

        return [min(validCards, key=lambda card: VALUES[card[0]])]

    '''
    Determines the AI player's move in medium mode by playing the most 
    strategic valid card based on the current game state.

    @param self - The instance of the AIPlayer class
    @param pile (list) - The pile to play cards onto
    @param deckSize (int) - The number of cards remaining in the deck
    @param playerTopCards (list) - The top cards of the player

    @return (list) - The card to play or -1 if the AI should pick up the pile

    @author Mike
    '''
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

    '''
    Determines the AI player's move in hard mode by playing the most strategic 
    valid card based on the current game state and prioritizing higher-ranked 
    cards if needed.

    @param self - The instance of the AIPlayer class
    @param pile (list) - The pile to play cards onto
    @param deckSize (int) - The number of cards remaining in the deck
    @param playerTopCards (list) - The top cards of the player

    @return (list) - The card to play or -1 if the AI should pick up the pile

    @author Mike
    '''
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

    '''
    Determines the AI player's move in impossible mode by always playing the 
    most optimal card to maximize winning chances.

    @param self - The instance of the AIPlayer class
    @param pile (list) - The pile to play cards onto
    @param deckSize (int) - The number of cards remaining in the deck
    @param playerTopCards (list) - The top cards of the player

    @return (list) - The card to play or -1 if the AI should pick up the pile

    @author Mike
    '''
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

    '''
    Checks if a card is playable based on the top card of the pile and the 
    sevenSwitch flag.

    @param self - The instance of the AIPlayer class
    @param card (tuple) - The card to check
    @param pile (list) - The current pile of cards

    @return (bool) - True if the card is playable, False otherwise

    @author Mike
    '''
    def isCardPlayable(self, card, pile):
        topCard = pile[-1] if pile else None
        if self.sevenSwitch:
            return VALUES[card[0]] <= 7 or card[0] in ['2', '10']
        if not topCard:
            return True
        return card[0] == '2' or card[0] == '10' or VALUES[card[0]] >= VALUES[topCard[0]]

    '''
    AI player selects the top three cards to place face-up.

    @param self - The instance of the AIPlayer class

    @return None

    @author Mike
    '''
    def chooseTopCards(self):
        sortedHand = sorted(self.hand, key=lambda card: VALUES[card[0]])
        for card in sortedHand[:3]:
            self.topCards.append((card[0], card[1], True, False))
        self.hand = sortedHand[3:]