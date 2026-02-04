from main import Deck, Card
import time

#--------------------------
# Create and shuffle the deck
#----------------------------
deck = Deck()
print("Shuffling and dealing...")
deck.shuffle()

# Deal 2 hole cards
player_hand = deck.deal(2)
print("Your cards:", player_hand[0], "and", player_hand[1])