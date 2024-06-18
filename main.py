import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Define card ranks and values
RANKS = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
VALUES = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'J': 10, 'Q': 11, 'K': 12, 'A': 13, '2': 14, '10': 15}

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.face_up = []
        self.face_down = []
        self.bottom_cards = []
        self.top_cards = []
        self.sevenSwitch = False  # Flag to restrict playable cards to 7 and lower or 2/10 for one turn

    def play_card(self, card_index, pile):
        card = self.hand.pop(card_index)
        pile.append(card)
        if card == '10':
            pile.clear()  # Clear the pile if a 10 is played
        elif card == '7':
            self.sevenSwitch = True  # Set flag to restrict next turn's playable cards
        return card

    def add_to_hand(self, cards):
        self.hand.extend(cards)

    def pick_up_pile(self, pile):
        self.hand.extend(pile)
        pile.clear()

    def has_playable_cards(self, top_pile):
        if self.sevenSwitch:
            return any(VALUES[card] <= 7 or card in ['2', '10'] for card in self.hand)
        else:
            return any(VALUES[card] >= VALUES[top_pile[-1]] for card in self.hand)

class AIPlayer(Player):
    def __init__(self):
        super().__init__("AI")

    def play_turn(self, pile):
        if not pile:
            return self.hand.index(min(self.hand, key=lambda card: VALUES[card]))
        if self.sevenSwitch:
            valid_cards = [card for card in self.hand if VALUES[card] <= 7 or card in ['2', '10']]
        else:
            valid_cards = [card for card in self.hand if VALUES[card] >= VALUES[pile[-1]] or card in ['2', '10']]
        if valid_cards:
            card_index = self.hand.index(min(valid_cards, key=lambda card: VALUES[card]))
            played_card = self.hand[card_index]
            if played_card == '2':
                self.sevenSwitch = False
            return card_index
        else:
            return -1
        
    def add_to_hand(self, cards):
        self.hand.extend(cards)    
        
    def pick_up_pile(self, pile):
        self.hand.extend(pile)
        pile.clear()
            
    def choose_top_cards(self):
        sorted_hand = sorted(self.hand, key=lambda card: VALUES[card])
        self.top_cards = sorted_hand[:3]
        self.hand = sorted_hand[3:]

class PalaceGame(QWidget):
    def __init__(self, num_players):
        super().__init__()
        self.num_players = num_players
        self.players = []
        self.deck = []
        self.pile = []
        self.current_player_index = 0
        self.init_ui()
        self.setup_game()

    def init_ui(self):
        self.setWindowTitle('Palace Card Game')
        self.setGeometry(100, 100, 1000, 800)
        self.layout = QVBoxLayout()
        
        # Opponent cards (backs)
        self.opponent_card_labels = []
        opponent_cards_layout = QHBoxLayout()
        for _ in range(self.num_players - 1):
            card_label = QLabel()
            card_label.setFixedSize(100, 150)
            card_label.setStyleSheet("border: 2px solid black; background-color: lightblue;")
            opponent_cards_layout.addWidget(card_label)
            self.opponent_card_labels.append(card_label)
        self.layout.addLayout(opponent_cards_layout)

        # Current player's cards (face up and hand)
        self.current_player_label = QLabel()
        self.current_player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.current_player_label)
        self.hand_scene = QGraphicsScene()
        self.hand_view = QGraphicsView(self.hand_scene)
        self.layout.addWidget(self.hand_view)

        # Draw deck and pile labels
        self.deck_label = QLabel()
        self.layout.addWidget(self.deck_label)
        self.pile_label = QLabel()
        self.pile_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.pile_label)

        # Pick up pile button
        self.pick_up_pile_button = QPushButton("Pick Up Pile")
        self.pick_up_pile_button.clicked.connect(self.pick_up_pile)
        self.layout.addWidget(self.pick_up_pile_button)

        # Play card buttons
        self.play_card_buttons = []
        self.play_buttons_layout = QHBoxLayout()
        for i in range(6):
            button = QPushButton()
            button.clicked.connect(lambda checked, idx=i: self.play_card(idx))
            self.play_buttons_layout.addWidget(button)
            self.play_card_buttons.append(button)
        self.layout.addLayout(self.play_buttons_layout)

        # Top cards layout
        self.top_cards_layout = QHBoxLayout()
        self.layout.addLayout(self.top_cards_layout)

        # Bottom cards layout
        self.bottom_cards_layout = QHBoxLayout()
        self.layout.addLayout(self.bottom_cards_layout)
        
        self.setLayout(self.layout)

    def pick_up_pile(self):
        current_player = self.players[self.current_player_index]
        current_player.pick_up_pile(self.pile)
        self.pile = []
        current_player.sevenSwitch = False
        self.change_turn()

    def change_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.update_ui()
        if isinstance(self.players[self.current_player_index], AIPlayer):
            self.ai_play_turn()

    def setup_game(self):
        self.players.append(Player("Player"))
        for _ in range(self.num_players - 1):
            self.players.append(AIPlayer())

        self.deck = self.create_deck()
        random.shuffle(self.deck)

        self.deal_initial_cards()
        self.choose_top_cards()  # Ask player to select top cards
        self.update_ui()

    def create_deck(self):
        return [rank for rank in RANKS * 4]  # Standard 52-card deck

    def deal_initial_cards(self):
        for player in self.players:
            player.bottom_cards = self.deck[:3]
            player.hand = self.deck[3:9]
            self.deck = self.deck[9:]

    def choose_top_cards(self):
        player = self.players[0]  # Assuming player is always the first in the list
        chosen_cards = []
        while len(chosen_cards) < 3:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Select Top Cards")
            msg_box.setText(f"Choose card {len(chosen_cards) + 1} to add to top cards:")
            for card in player.hand:
                button = msg_box.addButton(card, QMessageBox.ButtonRole.ActionRole)
                button.clicked.connect(lambda checked, card=card: chosen_cards.append(card))
            msg_box.exec()
        player.top_cards = chosen_cards
        for card in chosen_cards:
            player.hand.remove(card)
            
        # AI selects top cards
        for AIPlayer in self.players[1:]:
            AIPlayer.choose_top_cards()
        self.update_top_cards_buttons()
        self.update_bottom_cards_buttons()

    def update_top_cards_buttons(self):
        for i in reversed(range(self.top_cards_layout.count())):
            self.top_cards_layout.itemAt(i).widget().deleteLater()

        for card in self.players[0].top_cards:
            button = QPushButton(f"Top {card}")
            button.setEnabled(False)
            self.top_cards_layout.addWidget(button)

    def update_bottom_cards_buttons(self):
        for i in reversed(range(self.bottom_cards_layout.count())):
            self.bottom_cards_layout.itemAt(i).widget().deleteLater()

        for _ in self.players[0].bottom_cards:
            button = QPushButton("Bottom")
            button.setEnabled(False)
            self.bottom_cards_layout.addWidget(button)

    def update_ui(self):
        current_player = self.players[self.current_player_index]
        self.current_player_label.setText(f"Current Player: {current_player.name}")

        if self.pile:
            top_card = self.pile[-1]
            self.pile_label.setText(f"Pile Top Card: {top_card}")
        else:
            self.pile_label.setText("Pile: Empty")

        for i, label in enumerate(self.opponent_card_labels):
            label.setText(f"Opponent {i+1}'s Cards")

        self.hand_scene.clear()
        for i, card in enumerate(current_player.hand):
            card_label = QGraphicsPixmapItem(QPixmap(f"card_{card}.png"))  # Placeholder image
            card_label.setPos(i * 120, 0)
            self.hand_scene.addItem(card_label)

        self.hand_view.setScene(self.hand_scene)

        if self.deck:
            self.deck_label.setText(f"Draw Deck: {len(self.deck)} cards remaining")
        else:
            self.deck_label.setText("Draw Deck: Empty")

        self.update_play_buttons(len(current_player.hand))

        for i, card in enumerate(current_player.hand):
            if not self.is_card_playable(card):
                self.play_card_buttons[i].setEnabled(False)
            else:
                self.play_card_buttons[i].setEnabled(True)

        if isinstance(current_player, AIPlayer):
            self.ai_play_turn()

    def is_card_playable(self, card):
        if not self.pile:
            return True

        top_card = self.pile[-1]

        if self.players[self.current_player_index].sevenSwitch:
            return VALUES[card] <= 7 or card in ['2', '10']
        else:
            return VALUES[card] >= VALUES[top_card] or card in ['2', '10']

    def update_play_buttons(self, num_cards):
        for button in self.play_card_buttons:
            button.deleteLater()
        self.play_card_buttons.clear()

        for i in range(num_cards):
            card_rank = self.players[self.current_player_index].hand[i]
            button = QPushButton(f"Play {card_rank}")
            button.clicked.connect(lambda checked, idx=i: self.play_card(idx))
            self.play_buttons_layout.addWidget(button)
            self.play_card_buttons.append(button)

    def play_card(self, card_index):
        current_player = self.players[self.current_player_index]
        played_card = current_player.play_card(card_index, self.pile)
        print(f"{current_player.name} plays {played_card}")

        # Draw cards if fewer than 3 in hand
        while len(current_player.hand) < 3 and self.deck:
            current_player.hand.append(self.deck.pop(0))
        self.check_game_state()
        self.update_ui()
        if played_card in ['2', '10']:
            self.players[self.current_player_index].sevenSwitch = False
            self.check_game_state()
            self.update_ui()
        else:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if played_card == '7':
                self.players[self.current_player_index].sevenSwitch = True
            else:
                self.players[self.current_player_index].sevenSwitch = False
            self.check_game_state()
            self.update_ui()

        if isinstance(self.players[self.current_player_index], AIPlayer):
            self.ai_play_turn()

    def ai_play_turn(self):
        ai_player = self.players[self.current_player_index]
        top_pile = self.pile[-1] if self.pile else None
        card_index = ai_player.play_turn(self.pile)

        if card_index == -1:
            ai_player.add_to_hand(self.pile)
            self.pile = []
            print(f"{ai_player.name} picks up the pile")
            self.change_turn()
        else:
            played_card = ai_player.play_card(card_index, self.pile)
            print(f"{ai_player.name} plays {played_card}")

            # Draw cards if fewer than 3 in hand
            while len(ai_player.hand) < 3 and self.deck:
                ai_player.hand.append(self.deck.pop(0))

            if played_card in ['2', '10']:
                self.players[self.current_player_index].sevenSwitch = False
                self.check_game_state()
                self.update_ui()
            else:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
                if played_card == '7':
                    self.players[self.current_player_index].sevenSwitch = True
                else:
                    self.players[self.current_player_index].sevenSwitch = False
                self.check_game_state()
                self.update_ui()

    def check_game_state(self):
        for player in self.players:
            if not player.hand:
                print(f"{player.name} wins!")
                self.pick_up_pile_button.setDisabled(True)
                return

def main():
    app = QApplication(sys.argv)
    game = PalaceGame(2)  # Adjust number of players as needed
    game.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
