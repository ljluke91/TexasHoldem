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
# inverse mapping for convenience (map 1 to 'A' for ace-low straights)
VALUE_TO_RANK = {v: k for k, v in RANK_TO_VALUE.items()}
VALUE_TO_RANK[1] = "A"
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

    # Check for straight flush / royal flush (find best 5-card straight flush per suit)
    best_sf_cards = None
    best_sf_seq = None
    
    for suit, suited_cards in suits.items():
        if len(suited_cards) >= 5:
            suited_values = sorted(set(RANK_TO_VALUE[c.rank] for c in suited_cards))

            # Ace to be high or low in straight flushes
            if 14 in suited_values:
                suited_values.append(1)
                suited_values = sorted(set(suited_values))

            # Find all straight sequences of 5+
            straight_sequences = []
            if suited_values:
                run_seq = [suited_values[0]]
                for v in suited_values[1:]:
                    if v == run_seq[-1] + 1:
                        run_seq.append(v)
                    else:
                        if len(run_seq) >= 5:
                            straight_sequences.append(run_seq[:])
                        run_seq = [v]
                if len(run_seq) >= 5:
                    straight_sequences.append(run_seq[:])

            # Pick the best straight flush (highest ending value)
            if straight_sequences:
                best_seq = max(straight_sequences, key=lambda s: s[-1])
                best_five_vals = best_seq[-5:]  # Take top 5 of sequence
                
                # Map values back to cards
                sf_cards = []
                for val in best_five_vals:
                    rank = 'A' if val == 1 else VALUE_TO_RANK[val]
                    for c in suited_cards:
                        if c.rank == rank and c not in sf_cards:
                            sf_cards.append(c)
                            break
                
                # Keep track of best across all suits
                if best_sf_cards is None or best_five_vals[-1] > best_sf_seq[-1]:
                    best_sf_cards = sf_cards
                    best_sf_seq = best_five_vals

    # Return the best straight flush if found
    if best_sf_cards:
        high_val = best_sf_seq[-1]
        high_rank = 'A' if high_val == 1 else VALUE_TO_RANK[high_val]
        high_ranks = ", ".join(c.rank for c in best_sf_cards)
        
        # Check for royal flush (10-J-Q-K-A)
        if set(best_sf_seq) == {10, 11, 12, 13, 14}:
            return "a royal flush"
        
        return f"straight flush - {high_rank} high with {high_ranks}"

    # Check for four of a kind
    if 4 in counts:
        quad_ranks = sorted(
            [rank for rank, count in rank_counts.items() if count == 4],
            key=lambda r: RANK_TO_VALUE[r],
            reverse=True,
        )
        quad_rank = quad_ranks[0]
        quad_cards = [c for c in cards if c.rank == quad_rank][:4]

        remaining = [c for c in cards if c.rank != quad_rank]
        kicker_card = max(remaining, key=lambda c: RANK_TO_VALUE[c.rank]) if remaining else None

        kicker_text = kicker_card.rank if kicker_card else "none"
        return f"four of a kind - {quad_rank}s with a {kicker_text} kicker"


    # Check for a full house (best trips + best pair)
    if (3 in counts and 2 in counts) or (counts.count(3) >= 2):
        # Find all ranks with 3+ cards (candidate trips)
        trips_candidates = [rank for rank, cnt in rank_counts.items() if cnt >= 3]
        trips_rank = max(trips_candidates, key=lambda r: RANK_TO_VALUE[r])
        
        # Find all ranks with 2+ cards that aren't the trips rank (candidate pairs)
        pair_candidates = [rank for rank, cnt in rank_counts.items() if cnt >= 2 and rank != trips_rank]
        
        if pair_candidates:
            pair_rank = max(pair_candidates, key=lambda r: RANK_TO_VALUE[r])
            
            trips_cards = [c for c in cards if c.rank == trips_rank][:3]
            pair_cards = [c for c in cards if c.rank == pair_rank][:2]
            
            best_hand = trips_cards + pair_cards
            return f"full house - {trips_rank}s over {pair_rank}s"
        else:
            # Fallback if no pair found (unlikely)
            return "a full house"
    # Check for flush (return best 5 flush cards)
    for suit, count in suit_counts.items():
        if count >= 5:
            suited_cards = sorted(
                [c for c in cards if c.suit == suit],
                key=lambda c: RANK_TO_VALUE[c.rank],
                reverse=True,
            )[:5]
            ranks = ", ".join(c.rank for c in suited_cards)
            return f"flush - {suited_cards[0].rank} high with {ranks}"
        
    # Check for a straight (find best 5-card straight, ace can be low or high)
    straight_sequences = []
    if values:
        run_seq = [values[0]]
        for v in values[1:]:
            if v == run_seq[-1] + 1:
                run_seq.append(v)
            else:
                if len(run_seq) >= 5:
                    straight_sequences.append(run_seq[:])
                run_seq = [v]
        if len(run_seq) >= 5:
            straight_sequences.append(run_seq[:])

    if straight_sequences:
        # pick the straight with the highest top card
        best_seq = max(straight_sequences, key=lambda s: s[-1])
        # take the top 5 values of that sequence (in case it's longer than 5)
        best_five_vals = best_seq[-5:]

        best_straight_cards = []
        for val in best_five_vals:
            if val == 1:
                target_rank = 'A'
            else:
                target_rank = VALUE_TO_RANK[val]
            # pick one card with that rank (avoid reusing cards)
            for c in cards:
                if c.rank == target_rank and c not in best_straight_cards:
                    best_straight_cards.append(c)
                    break

        high_val = best_five_vals[-1]
        high_rank = 'A' if high_val == 1 else VALUE_TO_RANK[high_val]
        high_ranks = ", ".join(c.rank for c in best_straight_cards)
        return f"straight - {high_rank} high with {high_ranks}"
    #-----------------------------------------------------------------------
    ### Check for 3 of a kind (with 2 highest kickers)
    #-----------------------------------------------------------------------
    if 3 in counts:
        trips_ranks = sorted(
            [rank for rank, count in rank_counts.items() if count == 3],
            key=lambda r: RANK_TO_VALUE[r],
            reverse=True,
        )
        trips_rank = trips_ranks[0]
        trips_card = [c for c in cards if c.rank == trips_rank][:3]

        kickers = sorted(
            [c for c in cards if c.rank not in {trips_rank}],
            key=lambda c: RANK_TO_VALUE[c.rank],
            reverse=True
        )[:2]

        best_hand = trips_card + kickers

        kicker_ranks = ", ".join(k.rank for k in kickers)
        return f"Three of a kind - {trips_rank}s with kickers {kicker_ranks}"
        
   
    #------------------------------------------------------------------------
    ### Check for two pair (handle cases with 2 or more pairs — pick top two)
    #------------------------------------------------------------------------
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
   
    #------------------------------------------------------
    ### Check for one pair
    #------------------------------------------------------
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
        return f"one pair - {top_pair_rank}s with kickers {kicker_ranks}"
    
    #------------------------------------------------------
    ### High Card - pick the best 5 cards
    #------------------------------------------------------
    # Sort all cards by rank (descending) and take top 5
    best_five = sorted(cards, key=lambda c: RANK_TO_VALUE[c.rank], reverse=True)[:5]
    highest_card = best_five[0]
    high_card_ranks = ", ".join(c.rank for c in best_five)
    
    return f"High Card - {highest_card.rank} high with {high_card_ranks}"