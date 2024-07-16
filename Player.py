
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

class Player:
    '''
    Initializes the Player class with a name, and sets up the player's hand, 
    bottom cards, top cards, and sevenSwitch flag.

    @param self - The instance of the Player class
    @param name (str) - The name of the player

    @return None

    @author Mike
    '''
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.bottomCards = []
        self.topCards = []
        self.sevenSwitch = False  # Flag to restrict playable cards to 7 and lower or 2/10 for one turn

    '''
    Plays a card from the player's hand and adds it to the pile.

    @param self - The instance of the Player class
    @param cardIndex (int) - The index of the card to play from the hand
    @param pile (list) - The pile to add the played card to

    @return card (tuple) - The card that was played

    @author Mike
    '''
    def playCard(self, cardIndex, pile):
        card = self.hand.pop(cardIndex)
        if card[2]:
            card = (card[0], card[1], False, False)
        pile.append(card)
        return card

    '''
    Adds a list of cards to the player's hand.

    @param self - The instance of the Player class
    @param cards (list) - The cards to add to the hand

    @return None

    @author Mike
    '''
    def addToHand(self, cards):
        self.hand.extend(cards)

    '''
    Picks up the entire pile and adds it to the player's hand.

    @param self - The instance of the Player class
    @param pile (list) - The pile to pick up

    @return None

    @author Mike
    '''
    def pickUpPile(self, pile):
        self.hand.extend(pile)
        pile.clear()

    '''
    Checks if the player has any playable cards based on the top card of the 
    pile and the sevenSwitch flag.

    @param self - The instance of the Player class
    @param topPile (list) - The pile to check the top card from

    @return (bool) - True if the player has playable cards, False otherwise

    @author Mike
    '''
    def hasPlayableCards(self, topPile):
        if self.sevenSwitch:
            return any(VALUES[card[0]] <= 7 or card[0] in ['2', '10'] for card in self.hand)
        else:
            return any(card[0] == '2' or VALUES[card[0]] >= VALUES[topPile[-1][0]] for card in self.hand)