import random
import sys

def parse_card(txt: str):
    if len(txt) == 2:
        parts = txt[0], txt[1]
    elif len(txt) == 3:
        parts = txt[:2], txt[2]
    else:
        raise Exception(f"Invalid card '{txt}'")

    RANKS = {"j": 11, "q": 12, "k": 13, "a": 14}
    SUITS = {"s": 0, "c": 1, "h": 2, "d": 3}
    try:
        rank = int(parts[0]) 
    except ValueError:
        rank = RANKS.get(parts[0].lower()) 

    suit = SUITS.get(parts[1])

    if suit is None or rank is None:
        raise Exception(f"Invalid card '{txt}'")

    return rank, suit


def forms_straight(ranks):
    last = ranks[0]
    for x in ranks[1:]:
        if x != last + 1:
            return False
        last = x
    return True

# Key:
# 0 - High card
# 1 - Pair
# 2 - Two pair
# 3 - Three of a kind
# 4 - Straight
# 5 - Flush
# 6 - Full house
# 7 - Four of a kind
# 8 - Straight flush
# 9 - Royal flush
def score_hand(hole, community):
    # cards = sorted(hole + community, lambda x: x[0])
    cards = hole + community

    rank_count = {}
    for x in cards:
        rank_count[x[0]] = rank_count.get(x[0], 0) + 1

    unique_ranks = sorted(list(rank_count.keys()))
    if unique_ranks[-1] == 14:
        unique_ranks.insert(0, 1)
    
    suit_count = {}
    for x in cards:
        suit_count[x[1]] = suit_count.get(x[1], 0) + 1

    three = False
    pairs = 0
    for x in rank_count:
        if rank_count[x] == 4:
            # Four of a kind and straight flush are mutually exclusive
            return 7
        elif rank_count[x] == 3:
            three = True 
        elif rank_count[x] == 2:
            pairs += 1

    flush = None
    for x in suit_count:
        if suit_count[x] == 5:
            flush = x
            break
    
    straights = []
    for i in range(max(len(unique_ranks) - 4, 0)):
        if forms_straight(unique_ranks[i:i+5]):
            straights.append(unique_ranks[i])

    if flush is not None:
        # straight flush check 
        for x in straights:
            is_sf = True
            for i in range(x, x + 5):
                rank = 14 if i == 1 else i
                found_card = False
                for card in cards:
                    if card[0] == rank and card[1] == flush:
                        found_card = True 
                        break
                
                if not found_card:
                    is_sf = False
                    break
            
            if is_sf:
                # Finally found a straight flush!
                if x == 10:
                    return 9 # Royal flush!
                return 8

    # Full house 
    if three and pairs > 0:
        return 6
    
    # Flush
    if flush is not None:
        return 5
    
    # Straight
    if len(straights) > 0:
        return 4

    # Three
    if three:
        return 3
    
    # Two pair
    if pairs >= 2:
        return 2

    # Pair
    if pairs == 1:
        return 1

    return 0


def simulate_round(hole, deck):
    idxs = []
    deck_size = len(deck)
    while len(idxs) < 5:
        idx = random.randint(0, deck_size - 1)
        if idx in idxs:
            continue
        idxs.append(idx)
    
    cards = [deck[i] for i in idxs]

    return score_hand(hole, cards)


NAMES = (
    "High card",
    "Pair",
    "Two pair",
    "Three of a kind",
    "Straight",
    "Flush",
    "Full house",
    "Four of a kind",
    "Straight flush",
    "Royal flush"
)

def main():
    hole_input = " ".join(sys.argv[1:])
    
    print(f"Hole: {hole_input}\n")

    hole = [parse_card(x.strip()) for x in hole_input.split(" ")]

    deck = []
    for suit in range(4):
        for rank in range(2, 15):
            skip_card = False
            for x in hole:
                if x[0] == rank and x[1] == suit:
                    skip_card = True
                    break
            
            if skip_card:
                continue

            deck.append((rank, suit))

    NUM_ROUNDS = 200000
    histogram = {}
    for i in range(10):
        histogram[i] = 0

    for i in range(NUM_ROUNDS):
        score = simulate_round(hole, deck)
        histogram[score] += 1

    total = sum(histogram.values())
    for x in histogram:
        print(f"{NAMES[x]:<16} \t {100 * histogram[x] / NUM_ROUNDS:.4f}% \t 1 in {(NUM_ROUNDS / histogram[x]) if histogram[x] != 0 else 0:.1f} \t {100 * total / NUM_ROUNDS:.2f}% cumulative \t 1 in {(NUM_ROUNDS / total) if total != 0 else 0:.1f}")
        total -= histogram[x]

if __name__ == "__main__":
    main()
