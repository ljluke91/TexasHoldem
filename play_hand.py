from deck import Deck, Card
from board import Board
import time
from winning_hands import best_hand_name

# #--------------------------
# # Create and shuffle the deck
# #----------------------------
deck = Deck()
print("Shuffling and dealing...")
deck.shuffle()

board = Board()

# # Deal 2 hole cards
player_hand = deck.deal(2)
print("Your cards:", player_hand[0], "and", player_hand[1])

# Running the community cards
print("Dealing the flop...")
time.sleep(3)
board.deal_flop(deck)
print("Flop:", board.cards[0], board.cards[1], board.cards[2])

print("Dealing the turn...")
time.sleep(3)
board.deal_turn(deck)
print("Turn:", board.cards[3])

print("Dealing the river...")
time.sleep(3)
board.deal_river(deck)
print("River:", board.cards[4])

# Print the full board
print("The board:", " ".join(str(c) for c in board.cards))

# Determine best hand
all_cards = player_hand + board.cards
print("You have", best_hand_name(all_cards))