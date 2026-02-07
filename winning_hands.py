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
    suits = {}
    for card in cards:
        rank = card.rank
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
        # grouping cards by suit (for straight flush)
        suits.setdefault(card.suit, []).append(card)
    #debugging - remove later
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

    # Check for straight flush / royal flush
    for suit, suited_cards in suits.items():
        if len(suited_cards) >= 5:
            suited_values = sorted(set(RANK_TO_VALUE[c.rank] for c in suited_cards))

            # Ace to be high or low in straight flushes
            if 14 in suited_values:
                suited_values.append(1)
                suited_values = sorted(set(suited_values))

            run = 1
            for i in range(1, len(suited_values)):
                if suited_values[i] == suited_values[i - 1] + 1:
                    run += 1
                    if run >= 5:
                        # Royal flush is specifically 10-J-Q-K-A
                        if {10, 11, 12, 13, 14}.issubset(set(suited_values)):
                            return "a royal flush"
                        return "a straight flush"
                else:
                    run = 1

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
    # Check for two pair (handle cases with 2 or more pairs — pick top two)
    if counts.count(2) >= 2:
        # Find ranks that form pairs, sort high->low and take top two
        pair_ranks = sorted(
            [rank for rank, count in rank_counts.items() if count == 2],
            key=lambda r: RANK_TO_VALUE[r],
            reverse=True,
        )[:2]

        top_pair_rank, second_pair_rank = pair_ranks[0], pair_ranks[1]

        # Collect the actual Card objects for each pair (2 cards each)
        top_pair_cards = [c for c in cards if c.rank == top_pair_rank][:2]
        second_pair_cards = [c for c in cards if c.rank == second_pair_rank][:2]

        # Find the kicker: highest card that isn't in either pair rank
        remaining = [c for c in cards if c.rank not in {top_pair_rank, second_pair_rank}]
        kicker_card = None
        if remaining:
            kicker_card = max(remaining, key=lambda c: RANK_TO_VALUE[c.rank])

        best_hand = top_pair_cards + second_pair_cards + ([kicker_card] if kicker_card else [])

        kicker_text = kicker_card.rank if kicker_card else "none"
        return f"two pair - {top_pair_rank}{top_pair_rank} and {second_pair_rank}{second_pair_rank} with a {kicker_text} kicker"
    
    # Check for one pair
    if counts.count(2) == 1:
        # Find which rank makes the pair
        pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
        # Sort by highest pair
        pair_ranks.sort(key=lambda r: RANK_TO_VALUE[r], reverse=True)

        top_pair_rank = pair_ranks[0]

        # Collect the actual Card objects for the pair
        top_pair_cards = [c for c in cards if c.rank == top_pair_rank][:2]

        # Find the top 3 kickers (highest cards that aren't the pair rank)
        kickers = sorted(
            [c for c in cards if c.rank not in {top_pair_rank}],
            key=lambda c: RANK_TO_VALUE[c.rank],
            reverse=True
        )[:3]

        best_hand = top_pair_cards + kickers

        kicker_ranks = ", ".join(k.rank for k in kickers)
        return f"one pair - {top_pair_rank} with kickers {kicker_ranks}"
        

    return "High Card"