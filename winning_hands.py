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
RANK_TO_VALUE = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 11, "Q": 12, "K": 13, "A": 14
}
def best_hand_name(cards):
    # Count suits
    suit_counts = {}
    rank_counts = {}
    for card in cards:
        rank = card.rank
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
    print(rank_counts)

    values = []
    for card in cards:
        values.append(RANK_TO_VALUE[card.rank])

    values = sorted(set(values))

    # Making the ace be 1 or 14 for high/low straights
    if 14 in values:
        values.append(1)
        values = sorted(set(values))

    for card in cards:
        suit = card.suit
        suit_counts[suit] = suit_counts.get(suit, 0) + 1

    ## Defining checks for hand ranks

        counts = list(rank_counts.values())

    # Check for four of a kind
    if 4 in counts:
        return "four of a kind"
    # Check for a full house
    if (3 in counts and 2 in counts) or (counts.count(3) >= 2):
         return "a full house"
    # Check for flush
    for suit in suit_counts:
        if suit_counts[suit] >= 5:
            return "a flush"
        
    # Check for a straight
    run = 1
    for i in range(1, len(values)):
        if values[i] == values[i - 1] + 1:
            run += 1
            if run >= 5:
                return "a straight"
        else:
            run = 1
    
    # Check for 3 of a kind
    if 3 in counts:
        return "three of a kind"
    # Check for two pair
    if counts.count(2) == 2:
        return "two pair"
    #  Check for one pair
    if 2 in counts:
        return "one pair"
        

    return "High Card"