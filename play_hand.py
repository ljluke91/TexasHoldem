from deck import Deck, Card
from board import Board
import time
from winning_hands import best_hand_name

#--------------------------
# Create and shuffle the deck
#----------------------------
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

## Printing the full board
print(
    "The board:",
    board.cards[0],
    board.cards[1],
    board.cards[2],
    board.cards[3],
    board.cards[4]
)

from winning_hands import best_hand_name
all_cards = player_hand + board.cards
print("You have", best_hand_name(all_cards))

# --------------------------------------------------------
## Rigged hand temporary testing straight

# player_hand = [Card("♣", "4"), Card("♠", "5")]
# board_cards = [Card("♥", "J"), Card("♦", "A"), Card("♠", "10"), Card("♥", "2"), Card("♣", "3")]

# all_cards = player_hand + board_cards

# print("Your cards:", player_hand[0], "and", player_hand[1])
# print("The board:", board_cards[0], board_cards[1], board_cards[2], board_cards[3], board_cards[4])
# print("You have", best_hand_name(all_cards))
# -----------------------------------------------------------------------------------

## Rigged hand temporary testing quads

# player_hand = [Card("♥", "A"), Card("♠", "A")]
# board_cards = [Card("♦", "A"), Card("♣", "A"), Card("♠", "K"), Card("♦", "10"), Card("♣", "5")]

# all_cards = player_hand + board_cards

# print("Your cards:", player_hand[0], "and", player_hand[1])
# print("The board:", board_cards[0], board_cards[1], board_cards[2], board_cards[3], board_cards[4])
# print("You have", best_hand_name(all_cards))
# ---------------------------------------------------------------------------------------