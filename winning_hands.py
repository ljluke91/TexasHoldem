#------------------------------------------
#Ranking the winning hands in order from worst to best
#------------------------------------------
HAND_RANKS = {
    "High Card": 1,
    "One Pair": 2,
    "Two Pair": 3,
    "Three of a Kind": 4,
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Four of a Kind": 8,
    "Straight Flush": 9,
    "Royal Flush": 10
    }
def best_hand_name(cards):
    # Count suits
    suit_counts = {}

    for card in cards:
        suit = card.suit
        suit_counts[suit] = suit_counts.get(suit, 0) + 1

    # Check for flush
    for suit in suit_counts:
        if suit_counts[suit] >= 5:
            return "a flush"

    return "High Card"