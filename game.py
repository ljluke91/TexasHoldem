from deck import Deck
from board import Board
from player import Player
from winning_hands import best_hand_name
import time
import threading

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
        
        # Tournament tracking
        self.finished_players = []  # List of (player, placement) tuples
        
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
                # Update active_indices since player folded
                active_indices = set(i for i, p in enumerate(self.players) if not p.is_folded)
                
                # Check if only one player left after fold
                if len(self.get_active_players()) == 1:
                    winner = self.get_active_players()[0]
                    print(f"\n{winner.name} wins! Everyone else folded.")
                    return winner
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
            active_players = self.get_active_players()
            all_acted = all(i in players_acted for i, p in enumerate(self.players) if not p.is_folded)
            bets_equal = all(
                p.bet_this_round == self.current_bet or p.is_all_in
                for p in active_players
            )
            
            if all_acted and bets_equal:
                print(f"Betting round complete. Pot: {self.pot}")
                return None  # Normal completion, no early winner
            
            # Move to next player
            current_player_index = (current_player_index + 1) % self.num_players
    
    def _get_player_action(self, player):
        """
        Prompt the player for their action with a 60-second timeout. Returns (action, amount).
        If player doesn't respond in time, they automatically fold.
        
        Args:
            player: The Player object whose turn it is
        
        Returns:
            Tuple of (action_string, amount_if_applicable)
        """
        print(f"\n{player.name}'s turn. Chips: {player.chips}, Amount to call: {self.current_bet - player.bet_this_round} (total pot: {self.pot})")
        print(f"Your hand: {player.hand[0]} {player.hand[1]}")
        
        # Show current hand evaluation if board has cards
        if len(self.board.cards) > 0:
            all_cards = player.hand + self.board.cards
            hand_evaluation = best_hand_name(all_cards)
            print(f"You have {hand_evaluation}")
        
        print(f"(You have 60 seconds to act)")
        
        # Use a simple input mechanism with timeout
        user_input_container = []
        timeout_event = threading.Event()
        
        def get_input():
            try:
                user_input = input(f"{player.name}, enter action (fold/check/call/raise <amount>): ").strip().lower()
                user_input_container.append(user_input)
            except:
                user_input_container.append("")
        
        input_thread = threading.Thread(target=get_input, daemon=True)
        input_thread.start()
        input_thread.join(timeout=60)  # Wait up to 60 seconds
        
        if not user_input_container:
            # If they can check, auto-check. Otherwise, auto-fold.
            if player.bet_this_round == self.current_bet:
                print(f"\n{player.name} took too long. Auto-checking.")
                return ("check", 0)
            else:
                print(f"\n{player.name} took too long. Auto-folding.")
                return ("fold", 0)
        
        user_input = user_input_container[0]
        
        while True:
            if user_input == "fold":
                return ("fold", 0)
            
            elif user_input == "check":
                # Can only check if the bet amount is already matched
                if player.bet_this_round == self.current_bet:
                    return ("check", 0)
                else:
                    print(f"Cannot check. You must call {self.current_bet - player.bet_this_round} or raise.")
                    user_input = input(f"{player.name}, enter action (fold/check/call/raise <amount>): ").strip().lower()
                    continue
            
            elif user_input == "call":
                amount_to_call = self.current_bet - player.bet_this_round
                if amount_to_call > player.chips:
                    # Player doesn't have enough to fully call - they go all-in
                    # and excess is refunded to the raiser
                    actual_amount = player.chips
                    excess = amount_to_call - actual_amount
                    
                    # Find the player who made the current bet and refund them
                    if excess > 0:
                        for p in self.players:
                            if p.bet_this_round == self.current_bet and p != player:
                                p.chips += excess
                                self.pot -= excess
                                break
                    
                    bet_placed = player.place_bet(actual_amount)
                    self.pot += bet_placed
                    print(f"{player.name} calls all-in for {bet_placed}. (All-in!)")
                    return ("call", actual_amount)
                return ("call", amount_to_call)
            
            elif user_input.startswith("raise") or user_input.startswith("bet"):
                parts = user_input.split()
                if len(parts) != 2:
                    print("Invalid format. Use 'raise <amount>' or 'bet <amount>'")
                    user_input = input(f"{player.name}, enter action (fold/check/call/raise <amount>): ").strip().lower()
                    continue
                try:
                    bet_amount = int(parts[1])
                    min_bet = max(self.big_blind, self.current_bet + self.big_blind) if self.current_bet > 0 else self.big_blind
                    if bet_amount < min_bet:
                        print(f"Bet must be at least {min_bet}")
                        user_input = input(f"{player.name}, enter action (fold/check/call/raise <amount>): ").strip().lower()
                        continue
                    if bet_amount > player.chips + player.bet_this_round:
                        print(f"Not enough chips. Max bet is {player.chips + player.bet_this_round}")
                        user_input = input(f"{player.name}, enter action (fold/check/call/raise <amount>): ").strip().lower()
                        continue
                    return ("raise", bet_amount)
                except ValueError:
                    print("Invalid amount. Enter a number.")
                    user_input = input(f"{player.name}, enter action (fold/check/call/raise <amount>): ").strip().lower()
                    continue
            
            else:
                print("Invalid action. Use fold, check, call, or raise <amount>")
                user_input = input(f"{player.name}, enter action (fold/check/call/raise <amount>): ").strip().lower()
    
    def reset_bets_for_new_round(self):
        """Reset bet trackers for all players before the next betting round (flop/turn/river)"""
        for player in self.players:
            player.reset_bet_for_new_round()
        self.current_bet = 0
    
    def deal_flop(self):
        """Deal the flop (3 community cards)"""
        print("\n--- Dealing the Flop ---")
        self.board.deal_flop(self.deck)
        print(f"Flop: {self.board.cards[0]} {self.board.cards[1]} {self.board.cards[2]}")
        time.sleep(3)
    
    def deal_turn(self):
        """Deal the turn (4th community card)"""
        print("\n--- Dealing the Turn ---")
        self.board.deal_turn(self.deck)
        print(f"Board: {' '.join(str(c) for c in self.board.cards)}")
        time.sleep(3)
    
    def deal_river(self):
        """Deal the river (5th community card)"""
        print("\n--- Dealing the River ---")
        self.board.deal_river(self.deck)
        print(f"Board: {' '.join(str(c) for c in self.board.cards)}")
        time.sleep(3)
    
    def show_board(self):
        """Display all community cards"""
        if len(self.board.cards) > 0:
            print(f"Board: {' '.join(str(c) for c in self.board.cards)}")
    
    def evaluate_hands(self):
        """
        Evaluate all remaining (non-folded) players' hands.
        
        Returns:
            Dictionary: {player: hand_name, player: hand_name, ...}
        """
        hands = {}
        for player in self.get_active_players():
            all_cards = player.hand + self.board.cards
            hand_name = best_hand_name(all_cards)
            hands[player] = hand_name
        return hands
    
    def determine_winner(self):
        """
        Determine the winner based on best hand evaluation.
        
        Returns:
            Player object who wins the pot
        """
        active = self.get_active_players()
        if len(active) == 1:
            return active[0]
        
        # Evaluate all hands and find the best
        best_player = None
        best_hand_rank = 0
        
        for player in active:
            all_cards = player.hand + self.board.cards
            hand_name = best_hand_name(all_cards)
            
            # Map hand names to rank values for comparison
            hand_rank = self._get_hand_rank(hand_name)
            
            if hand_rank > best_hand_rank:
                best_hand_rank = hand_rank
                best_player = player
        
        return best_player
    
    def _get_hand_rank(self, hand_name):
        """Convert hand name to numeric rank for comparison. Returns highest rank found in string."""
        rank_map = {
            "royal flush": 10,
            "straight flush": 9,
            "four of a kind": 8,
            "full house": 7,
            "flush": 6,
            "straight": 5,
            "three of a kind": 4,
            "two pair": 3,
            "one pair": 2,
            "high card": 1,
        }
        
        for hand_type, rank in rank_map.items():
            if hand_type in hand_name.lower():
                return rank
        return 0
    
    def distribute_pot(self, winner):
        """Award the pot to the winner"""
        winner.add_chips(self.pot)
        print(f"\n{winner.name} wins the pot of {self.pot}!")
        print(f"{winner.name} now has {winner.chips} chips.")
        time.sleep(20)
    
    def play_hand(self):
        """
        Play one complete hand of poker from start to finish.
        
        Returns:
            The Player object who won the hand
        """
        self.new_hand()
        print(f"\n{'='*60}")
        print(f"HAND #{self.hand_count}")
        print(f"{'='*60}")
        
        for player in self.players:
            print(f"{player.name} ({player.position}): {player.chips} chips")
        
        print("\n--- Hole Cards Dealt ---")
        for player in self.players:
            if not player.is_folded:
                print(f"{player.name}: {player.hand[0]} {player.hand[1]}")
        
        # Pre-flop betting
        early_winner = self.betting_round(
            starting_index=self.get_first_to_act_preflop(),
            round_name="PRE-FLOP"
        )
        
        if early_winner:
            self.distribute_pot(early_winner)
            self.rotate_dealer()
            return early_winner
        
        # Post-flop betting
        self.reset_bets_for_new_round()
        self.deal_flop()
        early_winner = self.betting_round(
            starting_index=self.get_first_to_act_postflop(),
            round_name="FLOP"
        )
        
        if early_winner:
            self.distribute_pot(early_winner)
            self.rotate_dealer()
            return early_winner
        
        # Turn betting
        self.reset_bets_for_new_round()
        self.deal_turn()
        early_winner = self.betting_round(
            starting_index=self.get_first_to_act_postflop(),
            round_name="TURN"
        )
        
        if early_winner:
            self.distribute_pot(early_winner)
            self.rotate_dealer()
            return early_winner
        
        # River betting
        self.reset_bets_for_new_round()
        self.deal_river()
        early_winner = self.betting_round(
            starting_index=self.get_first_to_act_postflop(),
            round_name="RIVER"
        )
        
        if early_winner:
            self.distribute_pot(early_winner)
            self.rotate_dealer()
            return early_winner
        
        # Showdown
        print("\n--- SHOWDOWN ---")
        hands = self.evaluate_hands()
        for player, hand in hands.items():
            print(f"{player.name}: {hand}")
        
        winner = self.determine_winner()
        self.distribute_pot(winner)
        self.rotate_dealer()
        return winner
    
    def __str__(self):
        player_info = "\n".join([str(p) for p in self.players])
        return f"Poker Game (Hand #{self.hand_count}):\nPot: {self.pot}\nCurrent Bet: {self.current_bet}\n{player_info}"
