import random

# -------------------------------
# Class representing a single card
# -------------------------------
class Card:
    def __init__(self, suit, rank):
        self.suit = suit  # Store the suit (Hearts, Diamonds, Clubs, Spades)
        self.rank = rank  # Store the rank (2-10, J, Q, K, A)

    # Full display, for hole cards
    def __str__(self):
        return f"{self.rank}{self.suit}"

    

# -------------------------------
# Class representing a full deck
# -------------------------------
class Deck:
    def __init__(self):
        self.cards = []  # List to hold all 52 cards

        suits = ["♥", "♦", "♣", "♠"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

        # Build the deck
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))

    # Shuffle the deck
    def shuffle(self):
        random.shuffle(self.cards)

    # Deal n cards from the top
    def deal(self, n=1):
        dealt_cards = [self.cards.pop() for _ in range(n)]
        return dealt_cards