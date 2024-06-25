import sys
import random
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QCoreApplication, QTimer
import qdarktheme

# Dark Mode Styling
Dark = qdarktheme.load_stylesheet(
            theme="dark",
            custom_colors=
            {
                "[dark]": 
                {
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
        """

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
CARD_WIDTH = 70
CARD_HEIGHT = 105
BUTTON_WIDTH = 76
BUTTON_HEIGHT = 111

class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Palace')
        self.setGeometry(660, 215, 600, 500)
        layout = QVBoxLayout()
        title = QLabel("Palace")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: bold;")
        layout.addWidget(title)
        
        button_layout = QVBoxLayout()
        
        button_layout.addWidget(QLabel(""))
        button_layout.addWidget(QLabel(""))
        
        play_button = QPushButton("Play")
        play_button.setFixedHeight(45)
        play_button.setFixedWidth(250)
        play_button.clicked.connect(self.start_game)
        button_layout.addWidget(play_button)
        
        button_layout.addWidget(QLabel(""))
        button_layout.addWidget(QLabel(""))
        
        rules_button = QPushButton("Rules")
        rules_button.clicked.connect(self.show_rules)
        button_layout.addWidget(rules_button)
        
        button_layout.addWidget(QLabel(""))
        
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(QCoreApplication.instance().quit)
        button_layout.addWidget(exit_button)
        
        button_layout.addWidget(QLabel(""))
        
        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(button_container)

        self.setLayout(layout)

    def start_game(self):
        self.hide()
        controller = GameController(2)  # Start game with 2 players
        controller.view.show()

    def show_rules(self):
        rules_dialog = QDialog(self)
        rules_dialog.setWindowTitle("Rules")
        rules_dialog.setGeometry(760, 300, 400, 300)
        layout = QVBoxLayout()
        rules_label = QLabel("Rules of the game will be displayed here.")
        layout.addWidget(rules_label)
        close_button = QPushButton("Close")
        close_button.clicked.connect(rules_dialog.accept)
        layout.addWidget(close_button)
        rules_dialog.setLayout(layout)
        rules_dialog.exec()

class ChooseTopCardsDialog(QDialog):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.chosen_cards = []
        self.card_buttons = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Choose Top Cards')
        self.setGeometry(610, 270, 600, 400)
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

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.bottom_cards = []
        self.top_cards = []
        self.sevenSwitch = False  # Flag to restrict playable cards to 7 and lower or 2/10 for one turn
        self.bottom_cards_reached = False

    def play_card(self, card_index, pile):
        card = self.hand.pop(card_index)
        pile.append(card)
        return card

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

    def play_turn(self, pile, deck_size, player_top_cards):
        if not pile:
            return [self.hand.index(min(self.hand, key=lambda card: VALUES[card[0]]))]

        if self.sevenSwitch:
            valid_cards = [card for card in self.hand if VALUES[card[0]] <= 7 or card[0] in ['2', '10']]
        else:
            valid_cards = [card for card in self.hand if card[0] == '2' or card[0] == '10' or VALUES[card[0]] >= VALUES[pile[-1][0]]]

        if valid_cards:
            # Sort valid cards with a priority: 2s and 10s first, then 7s, then others by value
            valid_cards.sort(key=lambda card: (card[0] != '2', card[0] != '10', card[0] != '7', VALUES[card[0]]))

            # Play 2s or 10s if available
            if valid_cards[0][0] in ['2', '10']:
                return [self.hand.index(card) for card in self.hand if card[0] == valid_cards[0][0]]

            # Play 7 if available and there's a strategic advantage
            if valid_cards[0][0] == '7':
                return [self.hand.index(card) for card in self.hand if card[0] == valid_cards[0][0]]

            # Play the highest value card if the pile is likely to be picked up soon
            if deck_size == 0 or len(player_top_cards) < 3:
                highest_value_card = max(valid_cards, key=lambda card: VALUES[card[0]])
                return [self.hand.index(card) for card in self.hand if card[0] == highest_value_card[0]]

            # Otherwise, play the lowest value card
            lowest_value_card = min(valid_cards, key=lambda card: VALUES[card[0]])
            return [self.hand.index(card) for card in self.hand if card[0] == lowest_value_card[0]]
        else:
            return -1
        
    def choose_top_cards(self):
        sorted_hand = sorted(self.hand, key=lambda card: VALUES[card[0]])
        self.top_cards = sorted_hand[:3]
        self.hand = sorted_hand[3:]

class GameView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Palace Card Game')
        self.setGeometry(450, 30, 1000, 500)
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
        self.pile_label = QLabel("Pile: Empty")
        self.pile_label.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.pile_label.setStyleSheet("border: 0px solid black; background-color: transparent;")
        self.pile_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(self.pile_label)
        self.pick_up_pile_button = QPushButton("Pick Up Pile")
        self.pick_up_pile_button.setFixedWidth(150)
        self.pick_up_pile_button.clicked.connect(self.controller.pick_up_pile)
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
        self.player_hand_layout = QHBoxLayout()
        self.layout.addLayout(self.player_hand_layout)

        # Play card buttons layout
        self.play_buttons_layout = QHBoxLayout()  # Initialize the layout for play buttons
        self.layout.addLayout(self.play_buttons_layout)
        
        # Place button
        self.place_button = QPushButton("Place")
        self.place_button.setEnabled(False)
        self.place_button.clicked.connect(self.controller.place_card)
        self.layout.addWidget(self.place_button)

        self.setLayout(self.layout)

    def update_hand(self, hand, layout, is_player=True):
        # Clear existing widgets in the given layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if is_player:
            self.controller.play_card_buttons = []  # Clear existing play card buttons

        for idx, card in enumerate(hand):
            card_label = QLabel()
            card_label.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            card_label.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards\{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            card_label.setPixmap(pixmap)
            card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if is_player:
                card_label.mousePressEvent = lambda event, idx=idx, lbl=card_label: self.controller.prepare_card_placement(idx, lbl)
                self.controller.play_card_buttons.append(card_label)
            layout.addWidget(card_label)

    def update_player_hand(self, hand):
        self.update_hand(hand, self.player_hand_layout, is_player=True)
        
    def update_ai_hand(self, hand):
        self.update_hand(hand, self.ai_hand_layout, is_player=False)

    def update_top_cards_buttons(self, top_cards):
        for i in reversed(range(self.top_cards_layout.count())):
            self.top_cards_layout.itemAt(i).widget().deleteLater()

        for card in top_cards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards\{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button.setDisabled(True)
            self.top_cards_layout.addWidget(button)

    def update_bottom_cards_buttons(self, bottom_cards):
        for i in reversed(range(self.bottom_cards_layout.count())):
            self.bottom_cards_layout.itemAt(i).widget().deleteLater()

        for card in bottom_cards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(r"C:\workspace\PalaceAppV2\cards\back.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bottom_cards_layout.addWidget(button)

    def update_ai_top_cards_buttons(self, top_cards):
        for i in reversed(range(self.ai_top_cards_layout.count())):
            self.ai_top_cards_layout.itemAt(i).widget().deleteLater()

        for card in top_cards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(f"cards/{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setDisabled(True)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ai_top_cards_layout.addWidget(button)

    def update_ai_bottom_cards_buttons(self, bottom_cards):
        for i in reversed(range(self.ai_bottom_cards_layout.count())):
            self.ai_bottom_cards_layout.itemAt(i).widget().deleteLater()

        for card in bottom_cards:
            button = QLabel()
            button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
            button.setStyleSheet("border: 0px solid black; background-color: transparent;")
            pixmap = QPixmap(r"C:\workspace\PalaceAppV2\cards\back.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            button.setPixmap(pixmap)
            button.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ai_bottom_cards_layout.addWidget(button)

    def update_ui(self, current_player, deck_size, pile):
        self.current_player_label.setText(f"Current Player: {current_player.name}")
        
        if deck_size:
            self.deck_label.setText(f"Draw Deck:\n\n{deck_size} cards remaining")
        else:
            self.deck_label.setText("Draw Deck:\n\nEmpty")

        if pile:
            top_card = pile[-1]
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{top_card[0].lower()}_of_{top_card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.pile_label.setPixmap(pixmap)
        
        self.place_button.setEnabled(len(self.controller.selected_cards) > 0)
    
    def reveal_card(self, card_label, card):
        pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{card[0].lower()}_of_{card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        card_label.setPixmap(pixmap)

class GameController:
    def __init__(self, num_players):
        self.view = GameView(self)
        self.num_players = num_players
        self.players = []
        self.deck = []
        self.pile = []
        self.current_player_index = 0
        self.selected_cards = []  # Track the selected cards and their buttons
        self.play_card_buttons = []  # Initialize play_card_buttons
        self.setup_game()
        self.start_game_loop()

    def start_game_loop(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(1000)  # Run the game loop every second

    def game_loop(self):
        current_player = self.players[self.current_player_index]
        if isinstance(current_player, AIPlayer):
            self.ai_play_turn()
        else:
            self.view.update_ui(current_player, len(self.deck), self.pile)

    def pick_up_pile(self):
        current_player = self.players[self.current_player_index]
        current_player.pick_up_pile(self.pile)
        self.pile = []
        print(f"{current_player.name} picks up the pile")
        self.view.pile_label.setText("Pile: Empty")
        current_player.sevenSwitch = False
        self.update_ui()
        QCoreApplication.processEvents()
        self.change_turn()

    def setup_game(self):
        self.players.append(Player("Player"))
        for _ in range(self.num_players - 1):
            self.players.append(AIPlayer())

        self.deck = self.create_deck()
        random.shuffle(self.deck)

        self.deal_initial_cards()
        self.choose_top_cards()  # Ask player to select top cards
        self.view.update_player_hand(self.players[0].hand)
        self.view.update_ai_hand(self.players[1].hand)
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
            self.view.update_top_cards_buttons(player.top_cards)
            self.view.update_bottom_cards_buttons(player.bottom_cards)
        else:
            quit()
            
        # AI selects top cards
        for ai_player in self.players[1:]:
            ai_player.choose_top_cards()
            self.view.update_ai_top_cards_buttons(ai_player.top_cards)
            self.view.update_ai_bottom_cards_buttons(ai_player.bottom_cards)

    def update_ui(self):
        current_player = self.players[self.current_player_index]
        self.view.update_ui(current_player, len(self.deck), self.pile)
        if isinstance(current_player, AIPlayer):
            self.view.update_ai_hand(current_player.hand)
            self.view.pick_up_pile_button.setDisabled(True)
        else:
            self.view.pick_up_pile_button.setDisabled(False)
            self.view.update_player_hand(current_player.hand)
            self.update_playable_cards()

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

        self.view.place_button.setEnabled(len(self.selected_cards) > 0)  # Enable place button if any card is selected

    def is_card_playable(self, card):
        top_card = self.pile[-1] if self.pile else None
        if self.players[self.current_player_index].sevenSwitch:
            return VALUES[card[0]] <= 7 or card[0] in ['2', '10']
        if not top_card:
            return True  # Any card is playable if the pile is empty
        return card[0] == '2' or card[0] == '10' or VALUES[card[0]] >= VALUES[top_card[0]]

    def place_card(self):
        player = self.players[self.current_player_index]
        played_cards = []
        for card, button in sorted(self.selected_cards, key=lambda x: self.players[self.current_player_index].hand.index(x[0])):
            played_cards.append(card)
            player.play_card(self.players[self.current_player_index].hand.index(card), self.pile)
            self.view.reveal_card(button, card)
            button.setParent(None)  # Immediately remove the button from its parent
            button.deleteLater()  # Schedule it for deletion
        self.selected_cards = []  # Clear selected cards
        print(f"{player.name} plays {', '.join([f'{card[0]} of {card[1]}' for card in played_cards])}")

        # Draw cards if fewer than 3 in hand
        while len(player.hand) < 3 and self.deck:
            player.hand.append(self.deck.pop(0))

        self.view.update_player_hand(player.hand)  # Update the player hand layout

        # Update the state of playable cards
        self.update_playable_cards()

        # Check if 4 cards of the same rank in a row have been played
        if self.check_four_of_a_kind():
            print("Four of a kind! Clearing the pile.")
            self.pile.clear()
            self.view.pile_label.setText("Pile: Bombed")
            self.update_ui()
            self.check_game_state()
            return

        if '2' in [card[0] for card in played_cards]:
            self.players[self.current_player_index].sevenSwitch = False
            top_card = self.pile[-1]
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{top_card[0].lower()}_of_{top_card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.view.pile_label.setPixmap(pixmap)
            self.update_ui()
            self.check_game_state()
        elif '10' in [card[0] for card in played_cards]:
            self.pile.clear()
            self.players[self.current_player_index].sevenSwitch = False
            self.view.pile_label.setText("Pile: Bombed")
            self.update_ui()
            self.check_game_state()
        else:
            if '7' in [card[0] for card in played_cards]:
                self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = True
            else:
                self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = False
            self.view.place_button.setEnabled(False)
            top_card = self.pile[-1]
            pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{top_card[0].lower()}_of_{top_card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.view.pile_label.setPixmap(pixmap)
            self.change_turn()

    def ai_play_turn(self):
        time.sleep(2)
        ai_player = self.players[self.current_player_index]
        player_top_cards = self.players[0].top_cards  # Assuming player is always the first in the list
        played_cards = []
        card_indices = ai_player.play_turn(self.pile, len(self.deck), player_top_cards)
        if card_indices == -1:
            self.pick_up_pile()
            return
        else:
            card_indices = sorted(card_indices, reverse=True)
            for card_index in card_indices:
                played_card = ai_player.hand[card_index]
                ai_player.play_card(card_index, self.pile)
                played_cards.append(played_card)
                # Find the corresponding QLabel in the AI hand layout and reveal the card
                card_label = self.view.ai_hand_layout.itemAt(card_index).widget()
                self.view.reveal_card(card_label, played_card)
                card_label.setParent(None)
                card_label.deleteLater()  # Schedule it for deletion
            print(f"{ai_player.name} plays {', '.join([f'{card[0]} of {card[1]}' for card in played_cards])}")

            # Draw cards if fewer than 3 in hand
            while len(ai_player.hand) < 3 and self.deck:
                ai_player.hand.append(self.deck.pop(0))

            self.view.update_ai_hand(ai_player.hand)

            # Check if 4 cards of the same rank in a row have been played
            if self.check_four_of_a_kind():
                print("Four of a kind! Clearing the pile.")
                self.pile.clear()
                self.view.pile_label.setText("Pile: Bombed")
                self.update_ui()
                self.check_game_state()
                return

            if '2' in [card[0] for card in played_cards]:
                self.players[self.current_player_index].sevenSwitch = False
                if self.pile:
                    top_card = self.pile[-1]
                    pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{top_card[0].lower()}_of_{top_card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.view.pile_label.setPixmap(pixmap)
                else:
                    self.view.pile_label.setText("Pile: Empty")
                self.update_ui()
                self.check_game_state()
                return
            elif '10' in [card[0] for card in played_cards]:
                self.pile.clear()
                self.players[self.current_player_index].sevenSwitch = False
                self.view.pile_label.setText("Pile: Bombed")
                self.update_ui()
                self.check_game_state()
                return
            else:
                if '7' in [card[0] for card in played_cards]:
                    self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = True
                else:
                    self.players[(self.current_player_index + 1) % len(self.players)].sevenSwitch = False
                self.view.place_button.setEnabled(False)
                top_card = self.pile[-1]
                pixmap = QPixmap(fr"C:\workspace\PalaceAppV2\cards/{top_card[0].lower()}_of_{top_card[1].lower()}.png").scaled(CARD_WIDTH, CARD_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.view.pile_label.setPixmap(pixmap)
                self.update_ui()
                self.check_game_state()
                self.change_turn()
                return

    def change_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.selected_cards = []  # Clear selected cards on turn change
        self.update_ui()

    def check_four_of_a_kind(self):
        if len(self.pile) < 4:
            return False
        return len(set(card[0] for card in self.pile[-4:])) == 1

    def check_game_state(self):
        current_player = self.players[self.current_player_index]
        if not current_player.hand and not self.deck:
            if current_player.top_cards:
                current_player.hand = current_player.top_cards
                current_player.top_cards = []
                if isinstance(current_player, AIPlayer):
                    self.view.update_ai_hand(current_player.hand)
                    self.view.update_ai_top_cards_buttons(current_player.top_cards)
                else:
                    self.view.update_player_hand(current_player.hand)
                    self.view.update_top_cards_buttons(current_player.top_cards)
            elif current_player.bottom_cards:
                current_player.hand = current_player.bottom_cards
                current_player.bottom_cards = []
                if isinstance(current_player, AIPlayer):
                    self.view.update_ai_hand(current_player.hand)
                    self.view.update_ai_bottom_cards_buttons(self.players[1].bottom_cards)
                else:
                    self.view.update_player_hand(current_player.hand)
                    self.view.update_bottom_cards_buttons(current_player.bottom_cards)
            elif not current_player.bottom_cards:
                self.view.current_player_label.setText(f"{current_player.name} wins!")
                print(f"{current_player.name} wins!")
                self.view.pick_up_pile_button.setDisabled(True)
                self.view.place_button.setDisabled(True)

    def update_playable_cards(self):
        current_player = self.players[0]
        for i, lbl in enumerate(self.play_card_buttons):
            hand_card = current_player.hand[i]
            if self.is_card_playable(hand_card):
                lbl.setEnabled(True)
            else:
                lbl.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Dark)
    home_screen = HomeScreen()
    home_screen.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
