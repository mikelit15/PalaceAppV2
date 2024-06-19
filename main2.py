import sys
import random
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
                            QDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QCoreApplication

# Define card ranks and values
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
CARD_WIDTH = 70  
CARD_HEIGHT = 105 
BUTTON_WIDTH = 76  
BUTTON_HEIGHT = 111  

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
            return any(VALUES[card[0]] <= 7 or card[0] in ['2', '10'] for card in self.hand)
        else:
            return any(card[0] == '2' or VALUES[card[0]] >= VALUES[top_pile[-1][0]] for card in self.hand)

class AIPlayer(Player):
    def __init__(self):
        super().__init__("AI")

    def play_turn(self, pile):
        time.sleep(4)
        if not pile:
            return self.hand.index(min(self.hand, key=lambda card: VALUES[card[0]]))
        if self.sevenSwitch:
            valid_cards = [card for card in self.hand if VALUES[card[0]] <= 7 or card[0] in ['2', '10']]
        else:
            valid_cards = [card for card in self.hand if card[0] == '2' or VALUES[card[0]] >= VALUES[pile[-1][0]]]
        if valid_cards:
            card_index = self.hand.index(min(valid_cards, key=lambda card: VALUES[card[0]]))
            played_card = self.hand[card_index]
            if played_card[0] == '2':
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
        sorted_hand = sorted(self.hand, key=lambda card: VALUES[card[0]])
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
        self.setGeometry(600, 300, 600, 400)
        self.layout = QVBoxLayout()

        self.cards_layout = QHBoxLayout()
        for i, card in enumerate(self.player.hand):
            button = QLabel()
            button.setFixedSize(108, 151)  # Slightly wider than the image
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{card[0].lower()}_of_{card[1].lower()}.png").scaled(100, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button.mousePressEvent = lambda event, idx=i, btn=button: self.select_card(idx, btn)
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
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")  # Reset to default
        else:
            if len(self.chosen_cards) < 3:
                self.chosen_cards.append((card, card_index))
                button.setStyleSheet("border: 0px solid black; background-color: blue;")  # Highlight in light blue

        self.confirm_button.setEnabled(len(self.chosen_cards) == 3)
        self.undo_button.setEnabled(len(self.chosen_cards) > 0)

    def confirm_selection(self):
        self.accept()

    def undo_selection(self):
        if self.chosen_cards:
            last_selected_card, last_selected_index = self.chosen_cards.pop()
            for button in self.card_buttons:
                if self.card_buttons.index(button) == last_selected_index:
                    button.setStyleSheet("border: 0px solid black; background-color: transparent;")  # Reset to default
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
        self.selected_cards = []  # Track the selected cards and their buttons
        self.play_card_buttons = []  # Initialize play_card_buttons
        self.init_ui()
        self.setup_game()

    def init_ui(self):
        self.setWindowTitle('Palace Card Game')
        self.setGeometry(450, 50, 1000, 500)
        self.setFixedSize(1000, 1000)
        self.layout = QVBoxLayout()

        # AI player's hand
        self.ai_hand_layout = QHBoxLayout()
        self.layout.addLayout(self.ai_hand_layout)
        self.ai_player_label = QLabel("AI Player's Hand")
        self.ai_player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.ai_player_label)

        # AI player's top cards
        self.ai_top_cards_layout = QHBoxLayout()
        self.layout.addLayout(self.ai_top_cards_layout)

        # AI player's bottom cards
        self.ai_bottom_cards_layout = QHBoxLayout()
        self.layout.addLayout(self.ai_bottom_cards_layout)

        # Draw deck, Pile, and Pick Up Pile button layout
        center = QHBoxLayout()
        center.setSpacing(0)  # Set spacing to 0 to remove padding between widgets
        center.setContentsMargins(0, 0, 0, 0)  # Remove margins around the layout
        self.deck_label = QLabel()  # Initialize the deck label
        self.deck_label.setFixedWidth(150)
        center.addWidget(self.deck_label)
        self.pile_label = QLabel()
        self.pile_label.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.pile_label.setStyleSheet("border: 0px solid black; background-color: transparent;")
        self.pile_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(self.pile_label)
        self.pick_up_pile_button = QPushButton("Pick Up Pile")
        self.pick_up_pile_button.setFixedWidth(150)
        self.pick_up_pile_button.clicked.connect(self.pick_up_pile)
        center.addWidget(self.pick_up_pile_button)
        self.layout.addLayout(center)

        # Current player label
        self.current_player_label = QLabel("Current Player: Player")
        self.current_player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.current_player_label)

        # Player's bottom cards
        self.bottom_cards_layout = QHBoxLayout()  # Initialize bottom cards layout for the player
        self.layout.addLayout(self.bottom_cards_layout)

        # Player's top cards
        self.top_cards_layout = QHBoxLayout()  # Initialize top cards layout for the player
        self.layout.addLayout(self.top_cards_layout)

        # Player's hand
        self.player_hand_label = QLabel("Player's Hand")
        self.player_hand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.player_hand_label)
        self.player_hand_layout = QVBoxLayout()
        self.layout.addLayout(self.player_hand_layout)

        # Play card buttons layout
        self.play_buttons_layout = QHBoxLayout()  # Initialize the layout for play buttons
        self.layout.addLayout(self.play_buttons_layout)
        
        # Place button
        self.place_button = QPushButton("Place")
        self.place_button.setEnabled(False)
        self.place_button.clicked.connect(self.place_card)
        self.layout.addWidget(self.place_button)

        self.setLayout(self.layout)
    
    def pick_up_pile(self):
        current_player = self.players[self.current_player_index]
        current_player.pick_up_pile(self.pile)
        self.pile = []
        current_player.sevenSwitch = False
        self.change_turn()

    def change_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.selected_cards = []  # Clear selected cards on turn change
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
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        return [(rank, suit) for rank in RANKS for suit in suits]

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
            self.update_ai_top_cards_buttons(ai_player)
            self.update_ai_bottom_cards_buttons(ai_player)

    def update_top_cards_buttons(self):
        for i in reversed(range(self.top_cards_layout.count())):
            self.top_cards_layout.itemAt(i).widget().deleteLater()

        for card in self.players[0].top_cards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_cards_layout.addWidget(button)

    def update_bottom_cards_buttons(self):
        for i in reversed(range(self.bottom_cards_layout.count())):
            self.bottom_cards_layout.itemAt(i).widget().deleteLater()
        for _ in self.players[0].bottom_cards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(r"C:\workspace\PalaceAppV2\cards\back.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bottom_cards_layout.addWidget(button)

    def update_ai_top_cards_buttons(self, ai_player):
        for i in reversed(range(self.ai_top_cards_layout.count())):
            self.ai_top_cards_layout.itemAt(i).widget().deleteLater()

        for card in ai_player.top_cards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ai_top_cards_layout.addWidget(button)

    def update_ai_bottom_cards_buttons(self, ai_player):
        for i in reversed(range(self.ai_bottom_cards_layout.count())):
            self.ai_bottom_cards_layout.itemAt(i).widget().deleteLater()
        for _ in ai_player.bottom_cards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(r"C:\workspace\PalaceAppV2\cards\back.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ai_bottom_cards_layout.addWidget(button)

    def update_ui(self):
        current_player = self.players[self.current_player_index]
        self.current_player_label.setText(f"Current Player: {current_player.name}")
        if self.pile:
            top_card = self.pile[-1]
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{top_card[0].lower()}_of_{top_card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.pile_label.setPixmap(pixmap)
        else:
            self.pile_label.setText("Pile: Empty")
    
            # Update AI hand
            ai_player = self.players[1]  # Assuming AI player is the second player
            self.update_ai_hand(ai_player.hand)
            
            # Update current player hand
            player = self.players[0]
            self.update_player_hand(player.hand)

        if self.deck:
            self.deck_label.setText(f"Draw Deck:\n\n{len(self.deck)} cards remaining")
        else:
            self.deck_label.setText("Draw Deck:\n\nEmpty")

        self.update_play_buttons(len(current_player.hand))
        for i, card in enumerate(current_player.hand):
            if not self.is_card_playable(card):
                self.play_card_buttons[i].setEnabled(False)
            else:
                self.play_card_buttons[i].setEnabled(True)

        self.place_button.setEnabled(len(self.selected_cards) > 0)  # Ensure place button is enabled only if cards are selected

        if isinstance(current_player, AIPlayer):
            self.ai_play_turn()
        
    def is_card_playable(self, card):
        if not self.pile:
            return True
        top_card = self.pile[-1]
        if self.players[self.current_player_index].sevenSwitch:
            return VALUES[card[0]] <= 7 or card[0] in ['2', '10']
        else:
            return top_card[0] == '10' or card[0] == '2' or VALUES[card[0]] >= VALUES[top_card[0]] or card[0] == '10'

    def update_play_buttons(self, num_cards):
        for button in self.play_card_buttons:
            button.deleteLater()
        self.play_card_buttons.clear()
        for i in range(num_cards):
            card_rank, card_suit = self.players[self.current_player_index].hand[i]
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{card_rank.lower()}_of_{card_suit.lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button.mousePressEvent = lambda event, idx=i, btn=button: self.prepare_card_placement(idx, btn)
            self.play_buttons_layout.addWidget(button)
            self.play_card_buttons.append(button)
            
    def update_ai_hand(self, hand):
        # Clear existing widgets in the AI hand layout
        while self.ai_hand_layout.count() > 0:
            item = self.ai_hand_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            QCoreApplication.processEvents()

        # Update AI hand layout with current hand
        for card in hand:
            button = QLabel(f"{card[0]} of {card[1]}")
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ai_hand_layout.addWidget(button)
            QCoreApplication.processEvents()

    def update_player_hand(self, hand):
        # Clear existing widgets in the player hand layout
        while self.player_hand_layout.count() > 0:
            item = self.player_hand_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            QCoreApplication.processEvents()

        # Update player hand layout with current hand
        row_layout = QHBoxLayout()
        for i, card in enumerate(hand):
            if i > 0 and i % 12 == 0:  # Start a new row after every 12 cards
                self.player_hand_layout.addLayout(row_layout)
                row_layout = QHBoxLayout()
            card_label = QLabel()
            card_label.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            card_label.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards\{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            card_label.setPixmap(pixmap)
            card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_label.mousePressEvent = lambda event, idx=i, lbl=card_label: self.prepare_card_placement(idx, lbl)
            row_layout.addWidget(card_label)
            self.play_card_buttons.append(card_label)
        self.player_hand_layout.addLayout(row_layout)

    def prepare_card_placement(self, card_index, card_label):
        card = self.players[self.current_player_index].hand[card_index]
        
        if (card, card_label) in self.selected_cards:
            self.selected_cards.remove((card, card_label))
            card_label.setStyleSheet("border: 0px solid black; background-color: transparent;")  # Unhighlight the deselected card
        else:
            self.selected_cards.append((card, card_label))
            card_label.setStyleSheet("border: 0px solid black; background-color: blue;")  # Highlight selected card
        
        # Enable all buttons with the same rank, disable the rest
        selected_card_rank = card[0]
        if not self.selected_cards:
            for i, lbl in enumerate(self.play_card_buttons):
                hand_card = self.players[self.current_player_index].hand[i]
                if self.is_card_playable(hand_card):
                    lbl.setEnabled(True)
        else:
            for i, lbl in enumerate(self.play_card_buttons):
                hand_card = self.players[self.current_player_index].hand[i]
                if hand_card[0] == selected_card_rank or (hand_card, lbl) in self.selected_cards:
                    lbl.setEnabled(True)
                else:
                    lbl.setEnabled(False)

        self.place_button.setEnabled(len(self.selected_cards) > 0)  # Enable place button if any card is selected

    def place_card(self):
        current_player = self.players[self.current_player_index]
        played_cards = []
        for card, button in sorted(self.selected_cards, key=lambda x: self.players[self.current_player_index].hand.index(x[0])):
            played_cards.append(card)
            current_player.play_card(self.players[self.current_player_index].hand.index(card), self.pile)
            button.setStyleSheet("")  # Reset button style
            button.setEnabled(False)  # Disable button after playing
        
        self.selected_cards = []  # Clear selected cards
        print(f"{current_player.name} plays {', '.join([f'{card[0]} of {card[1]}' for card in played_cards])}")

        # Check if 4 cards of the same rank in a row have been played
        if self.check_four_of_a_kind():
            print("Four of a kind! Clearing the pile.")
            self.pile.clear()
            self.check_game_state()
            self.update_ui()
            return

        # Draw cards if fewer than 3 in hand
        while len(current_player.hand) < 3 and self.deck:
            current_player.hand.append(self.deck.pop(0))
        if '2' in [card[0] for card in played_cards]:
            self.players[self.current_player_index].sevenSwitch = False
            self.check_game_state()
            self.update_ui()
        elif '10' in [card[0] for card in played_cards]:
            self.pile.clear()
            self.players[self.current_player_index].sevenSwitch = False
            self.check_game_state()
            self.update_ui()
        else:
            if '7' in [card[0] for card in played_cards]:
                self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = True
            else:
                self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = False
            self.place_button.setEnabled(False)
            self.check_game_state()
            self.update_ui()
            QCoreApplication.processEvents()
            self.change_turn()

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
            print(f"{ai_player.name} plays {', '.join([f'{card[0]} of {card[1]}' for card in played_cards])}")

            # Check if 4 cards of the same rank in a row have been played
            if self.check_four_of_a_kind():
                print("Four of a kind! Clearing the pile.")
                self.pile.clear()

            # Draw cards if fewer than 3 in hand
            while len(ai_player.hand) < 3 and self.deck:
                ai_player.hand.append(self.deck.pop(0))

            if '2' in [card[0] for card in played_cards]:
                self.players[self.current_player_index].sevenSwitch = False
                self.check_game_state()
                self.update_ui()
            elif '10' in [card[0] for card in played_cards]:
                self.pile.clear()
                self.players[self.current_player_index].sevenSwitch = False
                self.check_game_state()
                self.update_ui()
            else:
                if '7' in [card[0] for card in played_cards]:
                    self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = True
                else:
                    self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = False
                self.place_button.setEnabled(True)
                self.check_game_state()
                self.update_ui()
                QCoreApplication.processEvents()
                self.change_turn()

    def check_four_of_a_kind(self):
        if len(self.pile) < 4:
            return False
        return len(set(card[0] for card in self.pile[-4:])) == 1

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

