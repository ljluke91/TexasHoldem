# Responsible for managing the community cards (flop, turn, river)
class Board:
    def __init__(self):
        self.cards = [] 

    def burn (self, deck):
        deck.deal(1)

    def deal_flop(self, deck):
        self.burn(deck)
        self.cards.extend(deck.deal(3))

    def deal_turn(self, deck):
        self.burn(deck)
        self.cards.extend(deck.deal(1))
        
    def deal_river(self, deck):
        self.burn(deck)
        self.cards.extend(deck.deal(1))