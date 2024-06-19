import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Define card ranks and values
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

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
        return [card]

    def add_to_hand(self, cards):
        self.hand.extend(cards)

    def pick_up_pile(self, pile):
        self.hand.extend(pile)
        pile.clear()

    def has_playable_cards(self, top_pile):
        if self.sevenSwitch:
            return any(VALUES[card] <= 7 or card in ['2', '10'] for card in self.hand)
        else:
            return any(card == '2' or VALUES[card] >= VALUES[top_pile[-1]] for card in self.hand)

class AIPlayer(Player):
    def __init__(self):
        super().__init__("AI")

    def play_turn(self, pile):
        if not pile:
            return self.hand.index(min(self.hand, key=lambda card: VALUES[card]))
        if self.sevenSwitch:
            valid_cards = [card for card in self.hand if VALUES[card] <= 7 or card in ['2', '10']]
        else:
            valid_cards = [card for card in self.hand if card == '2' or VALUES[card] >= VALUES[pile[-1]]]
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

class ChooseTopCardsDialog(QDialog):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.chosen_cards = []
        self.card_buttons = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Choose Top Cards')
        self.setGeometry(300, 300, 600, 200)
        self.layout = QVBoxLayout()

        self.cards_layout = QHBoxLayout()
        for i, card in enumerate(self.player.hand):
            button = QPushButton(card)
            button.clicked.connect(lambda checked, idx=i, btn=button: self.select_card(idx, btn))
            self.cards_layout.addWidget(button)
            self.card_buttons.append(button)

        self.layout.addLayout(self.cards_layout)

        self.buttons_layout = QHBoxLayout()
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.buttons_layout.addWidget(self.confirm_button)

        self.undo_button = QPushButton("Undo")
        self.undo_button.setEnabled(False)
        self.undo_button.clicked.connect(self.undo_selection)
        self.buttons_layout.addWidget(self.undo_button)

        self.layout.addLayout(self.buttons_layout)

        self.setLayout(self.layout)

    def select_card(self, card_index, button):
        card = self.player.hand[card_index]
        if (card, card_index) in self.chosen_cards:
            self.chosen_cards.remove((card, card_index))
            button.setStyleSheet("")  # Reset to default
        else:
            if len(self.chosen_cards) < 3:
                self.chosen_cards.append((card, card_index))
                button.setStyleSheet("background-color: lightblue; color: black;")  # Highlight in light blue with black text

        self.confirm_button.setEnabled(len(self.chosen_cards) == 3)
        self.undo_button.setEnabled(len(self.chosen_cards) > 0)

    def confirm_selection(self):
        self.accept()

    def undo_selection(self):
        if self.chosen_cards:
            last_selected_card, last_selected_index = self.chosen_cards.pop()
            for button in self.card_buttons:
                if self.card_buttons.index(button) == last_selected_index:
                    button.setStyleSheet("")  # Reset to default
                    button.setEnabled(True)
                    break

        self.confirm_button.setEnabled(len(self.chosen_cards) == 3)
        self.undo_button.setEnabled(len(self.chosen_cards) > 0)

class PalaceGame(QWidget):
    def __init__(self, num_players):
        super().__init__()
        self.num_players = num_players
        self.players = []
        self.deck = []
        self.pile = []
        self.current_player_index = 0
        self.selected_card_index = None  # Track the selected card index in hand
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
            button.clicked.connect(lambda checked, idx=i: self.prepare_card_placement(idx))
            self.play_buttons_layout.addWidget(button)
            self.play_card_buttons.append(button)
        self.layout.addLayout(self.play_buttons_layout)

        # Place card button
        self.place_button = QPushButton("Place")
        self.place_button.setEnabled(False)
        self.place_button.clicked.connect(self.place_card)
        self.layout.addWidget(self.place_button)

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
        dialog = ChooseTopCardsDialog(player)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            player.top_cards = [card for card, _ in dialog.chosen_cards]
            for card, card_index in sorted(dialog.chosen_cards, key=lambda x: x[1], reverse=True):
                del player.hand[card_index]  # Remove the specific card instance
            self.update_top_cards_buttons()
            self.update_bottom_cards_buttons()

        # AI selects top cards
        for ai_player in self.players[1:]:
            ai_player.choose_top_cards()

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
            return top_card == '10' or card == '2' or VALUES[card] >= VALUES[top_card] or card == '10'

    def update_play_buttons(self, num_cards):
        for button in self.play_card_buttons:
            button.deleteLater()
        self.play_card_buttons.clear()
        for i in range(num_cards):
            card_rank = self.players[self.current_player_index].hand[i]
            button = QPushButton(f"Play {card_rank}")
            button.clicked.connect(lambda checked, idx=i: self.prepare_card_placement(idx))
            self.play_buttons_layout.addWidget(button)
            self.play_card_buttons.append(button)

    def prepare_card_placement(self, card_index):
        self.selected_card_index = card_index
        selected_card = self.players[self.current_player_index].hand[card_index]
        self.place_button.setEnabled(True)
        self.update_hand_buttons_for_placement(selected_card)

    def update_hand_buttons_for_placement(self, selected_card):
        for i, button in enumerate(self.play_card_buttons):
            if self.players[self.current_player_index].hand[i] != selected_card:
                button.setEnabled(False)
            else:
                button.setStyleSheet("background-color: lightblue; color: black;")  # Highlight selected card in hand

    def place_card(self):
        current_player = self.players[self.current_player_index]
        played_cards = current_player.play_card(self.selected_card_index, self.pile)
        print(f"{current_player.name} plays {', '.join(played_cards)}")

        # Check if 4 cards of the same rank in a row have been played
        if self.check_four_of_a_kind():
            print("Four of a kind! Clearing the pile.")
            self.pile.clear()
            self.check_game_state()
            self.update_ui()

        # Draw cards if fewer than 3 in hand
        while len(current_player.hand) < 3 and self.deck:
            current_player.hand.append(self.deck.pop(0))
        if '2' in played_cards:
            self.players[self.current_player_index].sevenSwitch = False
            self.check_game_state()
            self.update_ui()
        elif '10' in played_cards:
            self.pile.clear()
            self.players[self.current_player_index].sevenSwitch = False
            self.check_game_state()
            self.update_ui()
        else:
            if '7' in played_cards:
                self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = True
            else:
                self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = False
            self.place_button.setEnabled(False)
            self.check_game_state()
            self.change_turn()
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
            played_cards = ai_player.play_card(card_index, self.pile)
            print(f"{ai_player.name} plays {', '.join(played_cards)}")

            # Check if 4 cards of the same rank in a row have been played
            if self.check_four_of_a_kind():
                print("Four of a kind! Clearing the pile.")
                self.pile.clear()

            # Draw cards if fewer than 3 in hand
            while len(ai_player.hand) < 3 and self.deck:
                ai_player.hand.append(self.deck.pop(0))

            if '2' in played_cards:
                self.players[self.current_player_index].sevenSwitch = False
                self.check_game_state()
                self.update_ui()
            elif '10' in played_cards:
                self.pile.clear()
                self.players[self.current_player_index].sevenSwitch = False
                self.check_game_state()
                self.update_ui()
            else:
                if '7' in played_cards:
                    self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = True
                else:
                    self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = False
                self.place_button.setEnabled(True)
                self.change_turn()
                self.check_game_state()
                self.update_ui()

    def check_four_of_a_kind(self):
        if len(self.pile) < 4:
            return False
        return len(set(self.pile[-4:])) == 1

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
