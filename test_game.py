"""
Simple test to play multiple hands of poker with 3 players.
This demonstrates the full game flow end-to-end.
"""

from player import Player
from game import PokerGame

# Create 3 players
alice = Player("Alice", 1000)
bob = Player("Bob", 1000)
charlie = Player("Charlie", 1000)

players = [alice, bob, charlie]

# Create game
game = PokerGame(players)

# Play multiple hands
hand_count = 0
while True:
    try:
        hand_count += 1
        winner = game.play_hand()
        
        print(f"\n{'='*60}")
        print(f"Hand #{hand_count} over! {winner.name} wins!")
        print(f"{'='*60}")
        print("\nChip counts:")
        for player in game.players:
            print(f"{player.name}: {player.chips} chips")
        
        # Check if anyone is busted out
        active_players = [p for p in players if p.chips > 0]
        if len(active_players) == 1:
            print(f"\n{active_players[0].name} wins the tournament!")
            break
        
    except KeyboardInterrupt:
        print("\n\nGame stopped by player.")
        break

print("\n--- Final Results ---")
for player in game.players:
    print(f"{player.name}: {player.chips} chips")
