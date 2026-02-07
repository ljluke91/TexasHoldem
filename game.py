from deck import Deck
from board import Board
from player import Player
from winning_hands import best_hand_name

class PokerGame:
    def __init__(self, players):
        """
        Initialize a poker game with a list of players.
        
        Args:
            players: List of Player objects (2-6 players)
        """
        if len(players) < 2 or len(players) > 6:
            raise ValueError("Poker game requires 2-6 players")
        
        self.players = players
        self.num_players = len(players)
        self.deck = None
        self.board = None
        self.pot = 0
        self.current_bet = 0  # The current bet amount players need to match
        
        # Blinds and positions
        self.dealer_index = 0  # Dealer position (rotates clockwise)
        self.small_blind = 10
        self.big_blind = 20
        self.hand_count = 0  # Track which hand we're on
        
        # Initialize positions
        self._update_positions()
    
    def _update_positions(self):
        """Update dealer, small blind, and big blind positions based on dealer_index"""
        for i, player in enumerate(self.players):
            if i == self.dealer_index:
                player.position = "D"  # Dealer
            elif i == (self.dealer_index + 1) % self.num_players:
                player.position = "SB"  # Small Blind
            elif i == (self.dealer_index + 2) % self.num_players:
                player.position = "BB"  # Big Blind
            else:
                player.position = i  # Regular position (numbered for reference)
    
    def new_hand(self):
        """Start a new hand: reset players, shuffle deck, deal cards"""
        # Reset all players for the new hand
        for player in self.players:
            player.reset_for_new_hand()
        
        # Reset game state
        self.deck = Deck()
        self.deck.shuffle()
        self.board = Board()
        self.pot = 0
        self.current_bet = 0
        self.hand_count += 1
        
        # Post blinds
        self._post_blinds()
        
        # Deal hole cards (2 to each player)
        for player in self.players:
            player.receive_cards(self.deck.deal(2))
    
    def _post_blinds(self):
        """Post small and big blinds to the pot"""
        sb_player = self.players[(self.dealer_index + 1) % self.num_players]
        bb_player = self.players[(self.dealer_index + 2) % self.num_players]
        
        # Place blinds
        sb_amount = sb_player.place_bet(self.small_blind)
        bb_amount = bb_player.place_bet(self.big_blind)
        
        self.pot += sb_amount + bb_amount
        self.current_bet = self.big_blind
        
        print(f"Blinds posted: {sb_player.name} (SB: {sb_amount}), {bb_player.name} (BB: {bb_amount})")
    
    def rotate_dealer(self):
        """Rotate dealer position clockwise for the next hand"""
        self.dealer_index = (self.dealer_index + 1) % self.num_players
        self._update_positions()
    
    def get_first_to_act_preflop(self):
        """Return the index of the player who acts first pre-flop (left of BB)"""
        return (self.dealer_index + 3) % self.num_players
    
    def get_first_to_act_postflop(self):
        """Return the index of the player who acts first post-flop (left of Dealer)"""
        return (self.dealer_index + 1) % self.num_players
    
    def get_active_players(self):
        """Return list of players who haven't folded"""
        return [p for p in self.players if not p.is_folded]
    
    def betting_round(self, starting_index=None, round_name=""):
        """
        Execute one betting round (pre-flop, post-flop, turn, or river).
        
        Args:
            starting_index: Index of the first player to act (determine via get_first_to_act_* methods)
            round_name: Name of the round (for display purposes)
        
        Returns:
            early_winner: Player object if everyone folded except one. None if betting completed normally.
        """
        if starting_index is None:
            starting_index = self.get_first_to_act_preflop()
        
        print(f"\n--- {round_name} Betting Round ---")
        
        # Track which players have acted in this round
        players_acted = set()
        
        # Before each round, reset bet trackers and mark all non-folded players as not acted
        active_indices = set(i for i, p in enumerate(self.players) if not p.is_folded)
        
        current_player_index = starting_index
        
        # Keep cycling through players until all have acted and bets are equal
        while True:
            # If only one player left (everyone else folded), they win
            if len(self.get_active_players()) == 1:
                winner = self.get_active_players()[0]
                print(f"\n{winner.name} wins! Everyone else folded.")
                return winner
            
            # Cycle to next active player
            while current_player_index not in active_indices:
                current_player_index = (current_player_index + 1) % self.num_players
            
            player = self.players[current_player_index]
            
            # Get player action
            action, amount = self._get_player_action(player)
            
            if action == "fold":
                player.fold()
                print(f"{player.name} folds.")
            elif action == "check":
                print(f"{player.name} checks.")
            elif action == "call":
                bet_placed = player.place_bet(amount)
                self.pot += bet_placed
                print(f"{player.name} calls {bet_placed}. (Chips left: {player.chips})")
            elif action == "raise":
                bet_placed = player.place_bet(amount)
                self.pot += bet_placed
                self.current_bet = amount  # Update the current bet to match
                print(f"{player.name} raises to {amount}. (Chips left: {player.chips})")
                players_acted.clear()  # Reset acted players when bet increases
            
            players_acted.add(current_player_index)
            
            # Check if all active players have acted and bets are equal
            # (accounting for all-in players — they're done betting even if betted less)
            all_acted = all(i in players_acted for i in active_indices)
            bets_equal = all(
                self.players[i].bet_this_round == self.current_bet or self.players[i].is_all_in
                for i in active_indices
            )
            
            if all_acted and bets_equal:
                print(f"Betting round complete. Pot: {self.pot}")
                return None  # Normal completion, no early winner
            
            # Move to next player
            current_player_index = (current_player_index + 1) % self.num_players
    
    def _get_player_action(self, player):
        """
        Prompt the player for their action. Returns (action, amount).
        
        Args:
            player: The Player object whose turn it is
        
        Returns:
            Tuple of (action_string, amount_if_applicable)
        """
        print(f"\n{player.name}'s turn. Chips: {player.chips}, Current bet to match: {self.current_bet}")
        print(f"Your hand: {player.hand[0]} {player.hand[1]}")
        
        while True:
            user_input = input(f"{player.name}, enter action (fold/check/call/raise <amount>): ").strip().lower()
            
            if user_input == "fold":
                return ("fold", 0)
            
            elif user_input == "check":
                # Can only check if the bet amount is already matched
                if player.bet_this_round == self.current_bet:
                    return ("check", 0)
                else:
                    print(f"Cannot check. You must call {self.current_bet - player.bet_this_round} or raise.")
                    continue
            
            elif user_input == "call":
                amount_to_call = self.current_bet - player.bet_this_round
                if amount_to_call > player.chips:
                    print(f"Not enough chips. You can only go all-in for {player.chips}.")
                    continue
                return ("call", amount_to_call)
            
            elif user_input.startswith("raise"):
                parts = user_input.split()
                if len(parts) != 2:
                    print("Invalid format. Use 'raise <amount>'")
                    continue
                try:
                    raise_amount = int(parts[1])
                    if raise_amount <= self.current_bet:
                        print(f"Raise must be more than current bet ({self.current_bet})")
                        continue
                    if raise_amount > player.chips + player.bet_this_round:
                        print(f"Not enough chips. Max raise is {player.chips + player.bet_this_round}")
                        continue
                    return ("raise", raise_amount)
                except ValueError:
                    print("Invalid amount. Enter a number.")
                    continue
            
            else:
                print("Invalid action. Use fold, check, call, or raise <amount>")
    
    def __str__(self):
        player_info = "\n".join([str(p) for p in self.players])
        return f"Poker Game (Hand #{self.hand_count}):\nPot: {self.pot}\nCurrent Bet: {self.current_bet}\n{player_info}"
