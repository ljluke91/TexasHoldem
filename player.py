# Player class representing a poker player at the table
class Player:
    def __init__(self, name, starting_chips=1000):
        self.name = name
        self.chips = starting_chips
        self.hand = []  # Two hole cards dealt at start of hand
        self.position = None  # Will be "D" (Dealer), "SB" (Small Blind), "BB" (Big Blind), or a position number
        self.is_folded = False  # Has this player folded this hand?
        self.bet_this_round = 0  # How much they've bet in the current round
        self.is_all_in = False  # Did this player go all-in?

    def reset_for_new_hand(self):
        """Reset the player's state for a new hand (keep chips, clear hand/bets)"""
        self.hand = []
        self.is_folded = False
        self.bet_this_round = 0
        self.is_all_in = False

    def receive_cards(self, cards):
        """Give the player their two hole cards"""
        self.hand = cards

    def fold(self):
        """Player folds this hand"""
        self.is_folded = True

    def place_bet(self, amount):
        """Player places a bet (removes chips from their stack and records the bet)"""
        if amount > self.chips:
            # All-in scenario
            amount = self.chips
            self.is_all_in = True
        
        self.chips -= amount
        self.bet_this_round += amount
        return amount

    def reset_bet_for_new_round(self):
        """Reset the bet counter for the next betting round (flop, turn, river)"""
        self.bet_this_round = 0

    def add_chips(self, amount):
        """Add chips to the player's stack (e.g., when they win the pot)"""
        self.chips += amount

    def __str__(self):
        return f"{self.name} (Position: {self.position}, Chips: {self.chips}, Hand: {self.hand})"
