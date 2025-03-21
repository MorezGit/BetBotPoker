# Final
import random
import time
from collections import Counter
from itertools import combinations

# ===== Card and Deck Classes =====
class Card:
    """Represents a single playing card."""
    suits = ["♠", "♥", "♦", "♣"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.rank = Card.values.index(value) + 2  # Numeric rank (2-14)
    
    def __repr__(self):
        return f"{self.value}{self.suit}"

class Deck:
    """Represents a deck of 52 shuffled cards."""
    def __init__(self):
        self.cards = [Card(suit, value) for suit in Card.suits for value in Card.values]
        random.shuffle(self.cards)
    
    def deal(self, num):
        """Deal num cards."""
        return [self.cards.pop() for _ in range(num)]

# ===== Player Class =====
class Player:
    """Represents a player in the game."""
    def __init__(self, name, chips=100000, is_human=False):
        self.name = name
        self.chips = chips
        self.hand = []
        self.active = True
        self.all_in = False
        self.current_bet = 0
        self.total_bet = 0
        self.is_human = is_human
    
    def reset_for_round(self):
        """Reset player state for new round."""
        self.hand = []
        self.active = True if self.chips > 0 else False
        self.all_in = False
        self.current_bet = 0
        self.total_bet = 0
    
    def chip_bar(self):
        """Graphical chip bar."""
        bar_length = int(self.chips / 5000)
        return "|" * bar_length if bar_length > 0 else "X"
    
    def __repr__(self):
        return f"{self.name} ({self.chips} chips)"

# ===== Hand Evaluator Class =====
class HandEvaluator:
    """Evaluates poker hands."""
    hand_ranks = {
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

    @staticmethod
    def evaluate_hand(cards):
        suits = [card.suit for card in cards]
        values = [card.rank for card in cards]
        value_counts = Counter(values)
        counts = value_counts.values()
        unique_vals = sorted(set(values), reverse=True)

        # Check Flush
        flush = None
        for suit in Card.suits:
            if suits.count(suit) >= 5:
                flush = [card for card in cards if card.suit == suit]
                flush = sorted(flush, key=lambda c: c.rank, reverse=True)
                break

        # Check Straight
        straight = None
        vals = sorted(set(values))
        if 14 in vals:
            vals.insert(0, 1)  # Ace-low straight
        for i in range(len(vals) - 4):
            if vals[i+4] - vals[i] == 4 and len(set(vals[i:i+5])) == 5:
                straight = vals[i+4]

        # Check Straight Flush / Royal Flush
        if flush:
            flush_vals = sorted(set(card.rank for card in flush))
            if 14 in flush_vals:
                flush_vals.insert(0, 1)
            for i in range(len(flush_vals) - 4):
                if flush_vals[i+4] - flush_vals[i] == 4 and len(set(flush_vals[i:i+5])) == 5:
                    if flush_vals[i+4] == 14:
                        return ("Royal Flush", [14])
                    else:
                        return ("Straight Flush", [flush_vals[i+4]])

        # Four of a Kind
        if 4 in counts:
            quad = value_counts.most_common(1)[0][0]
            kicker = max(v for v in values if v != quad)
            return ("Four of a Kind", [quad, kicker])

        # Full House
        if 3 in counts and 2 in counts:
            trips = value_counts.most_common(1)[0][0]
            pair = [v for v, c in value_counts.items() if c >= 2 and v != trips]
            return ("Full House", [trips, max(pair)])

        # Flush
        if flush:
            return ("Flush", [card.rank for card in flush[:5]])

        # Straight
        if straight:
            return ("Straight", [straight])

        # Three of a Kind
        if 3 in counts:
            trips = value_counts.most_common(1)[0][0]
            kickers = sorted([v for v in values if v != trips], reverse=True)[:2]
            return ("Three of a Kind", [trips] + kickers)

        # Two Pair
        pairs = [v for v, c in value_counts.items() if c == 2]
        if len(pairs) >= 2:
            top_two = sorted(pairs, reverse=True)[:2]
            kicker = max([v for v in values if v not in top_two])
            return ("Two Pair", top_two + [kicker])

        # One Pair
        if 2 in counts:
            pair = value_counts.most_common(1)[0][0]
            kickers = sorted([v for v in values if v != pair], reverse=True)[:3]
            return ("One Pair", [pair] + kickers)

        # High Card
        return ("High Card", sorted(values, reverse=True)[:5])
# ===== Helper Functions =====

def print_chip_bars(players):
    """Display graphical chip bars for each player."""
    print("\nCurrent Chips:")
    for p in players:
        print(f"{p.name}: {p.chip_bar()} ({p.chips})")
    print("-" * 30)

def deal_hands(players, deck):
    """Deal two cards to each player."""
    for p in players:
        p.hand = deck.deal(2)

def post_blinds(players, dealer_pos, small_blind, big_blind):
    """Post small and big blinds."""
    sb_player = players[(dealer_pos + 1) % len(players)]
    bb_player = players[(dealer_pos + 2) % len(players)]

    sb = min(small_blind, sb_player.chips)
    sb_player.chips -= sb
    sb_player.current_bet = sb
    sb_player.total_bet = sb

    bb = min(big_blind, bb_player.chips)
    bb_player.chips -= bb
    bb_player.current_bet = bb
    bb_player.total_bet = bb

    print(f"\n{sb_player.name} posts Small Blind: {sb}")
    print(f"{bb_player.name} posts Big Blind: {bb}")

    return sb + bb

def animate_board(board):
    """Animate displaying board cards."""
    print("\nBoard Cards:")
    for card in board:
        print(card, end=" ", flush=True)
        time.sleep(0.8)
    print("\n" + "-"*30)

def check_early_winner(players):
    """Check if only one player remains active."""
    active = [p for p in players if p.active]
    if len(active) == 1:
        return active[0]
    return None

def bot_dialogue(action):
    """Return a random bot dialogue based on action."""
    phrases = {
        "fold": ["Nah, not this hand.", "I'll pass.", "Not feeling lucky..."],
        "call": ["I'll call.", "Hmm... call.", "Let's see what happens."],
        "raise": ["Let me spice things up!", "I'm feeling bold!", "Raise it up!"],
        "all-in": ["ALL-IN, baby!", "Go big or go home!", "I'm all-in!"],
        "check": ["I'll check.", "No bet from me.", "Check."]
    }
    return random.choice(phrases[action])

def log_history(history, hand_num, players, board, pot, winner=None, win_hand=None):
    """Log summary of each hand."""
    entry = {
        "hand": hand_num,
        "players": [(p.name, p.chips) for p in players],
        "board": board.copy(),
        "pot": pot,
        "winner": winner.name if winner else None,
        "winning_hand": win_hand
    }
    history.append(entry)

def distribute_pot(players, pot, winner):
    """Distribute pot to winner."""
    print(f"\n🏆 {winner.name} wins {pot} chips!")
    winner.chips += pot

def show_hand_summary(history):
    """Display previous hand summary."""
    if not history:
        return
    last = history[-1]
    print("\n=== Previous Hand Summary ===")
    print(f"Winner: {last['winner']}")
    print(f"Pot: {last['pot']}")
    print(f"Board: {last['board']}")
    print(f"Winning Hand: {last['winning_hand']}")
    print("-"*35)

def betting_round(players, dealer_pos, min_bet, pot, board):
    current_bet = min_bet
    last_raiser = None
    round_done = False

    while not round_done:
        round_done = True
        for i in range(len(players)):
            player = players[(dealer_pos + 1 + i) % len(players)]
            if not player.active or player.all_in:
                continue

            to_call = current_bet - player.current_bet

            print_chip_bars(players)
            print(f"\n{player.name}'s turn - Pot: {pot}")
            animate_board(board)
            if player.is_human:
                print(f"Your hand: {player.hand}")

            time.sleep(1)

            # ===== Human Player =====
            if player.is_human:
                options = []
                if to_call == 0:
                    options.append("check")
                else:
                    options.append(f"call ({to_call})")
                if player.chips > to_call and not any(p.all_in for p in players if p != player):
                    options.append("raise")
                if player.chips > 0:
                    options.append("all-in")
                options.append("fold")

                print(f"Options: {', '.join(options)}")

                while True:
                    action = input("Choose action: ").lower()

                    if action.startswith("call") and to_call > 0:
                        call_amt = min(to_call, player.chips)
                        player.chips -= call_amt
                        player.current_bet += call_amt
                        player.total_bet += call_amt
                        pot += call_amt
                        print(f"You call {call_amt}.")
                        if player.chips == 0:
                            player.all_in = True
                            print("You are ALL-IN!")
                        time.sleep(1)
                        break

                    elif action == "check" and to_call == 0:
                        print("You checked.")
                        time.sleep(1)
                        break

                    elif action == "raise" and player.chips > to_call and not any(p.all_in for p in players if p != player):
                        while True:
                            try:
                                raise_amt = int(input(f"Enter raise amount (min {min_bet}): "))
                                if raise_amt >= min_bet and raise_amt <= player.chips - to_call:
                                    break
                            except:
                                continue
                        total_raise = to_call + raise_amt
                        player.chips -= total_raise
                        player.current_bet += total_raise
                        player.total_bet += total_raise
                        pot += total_raise
                        current_bet = player.current_bet
                        last_raiser = player
                        print(f"You raised to {current_bet}.")
                        round_done = False
                        time.sleep(1)
                        break

                    elif action == "all-in":
                        all_in_amt = player.chips
                        player.current_bet += all_in_amt
                        player.total_bet += all_in_amt
                        pot += all_in_amt
                        player.chips = 0
                        player.all_in = True
                        print(f"You go ALL-IN with {all_in_amt}!")
                        time.sleep(1)
                        break

                    elif action == "fold":
                        player.active = False
                        print("You folded.")
                        time.sleep(1)
                        break

                    else:
                        print("Invalid option. Please choose again.")

            # ===== Bot Players =====
            else:
                time.sleep(random.uniform(1.2, 2.0))  # Natural delay
                decision = "call"
                if player.chips <= to_call:
                    decision = "call"
                else:
                    r = random.random()
                    if r < 0.2:
                        decision = "fold"
                    elif r < 0.4 and not any(p.all_in for p in players if p != player):
                        decision = "raise"
                    else:
                        decision = "call"

                print(f"{player.name}: {bot_dialogue(decision)}")
                time.sleep(1)

                if decision == "fold":
                    player.active = False
                    print(f"{player.name} folds.")
                    time.sleep(1.2)
                    continue

                elif decision == "call":
                    call_amt = min(to_call, player.chips)
                    player.chips -= call_amt
                    player.current_bet += call_amt
                    player.total_bet += call_amt
                    pot += call_amt
                    if player.chips == 0:
                        player.all_in = True
                        print(f"{player.name} is ALL-IN!")
                    else:
                        print(f"{player.name} calls {call_amt}.")
                    time.sleep(1.2)

                elif decision == "raise":
                    raise_amt = min(min_bet * 2, player.chips - to_call)
                    total_raise = to_call + raise_amt
                    player.chips -= total_raise
                    player.current_bet += total_raise
                    player.total_bet += total_raise
                    pot += total_raise
                    current_bet = player.current_bet
                    last_raiser = player
                    print(f"{player.name} raises to {current_bet}.")
                    round_done = False
                    time.sleep(1.5)

            # ===== Early Winner Check =====
            remaining = [p for p in players if p.active]
            if len(remaining) == 1:
                return pot, True, remaining[0]
        
        # Check if betting round done
        if all((p.current_bet == current_bet or p.all_in or not p.active) for p in players):
            round_done = True

    # Reset current bets
    for p in players:
        p.current_bet = 0

    return pot, False, None

def determine_winner(players, board):
    """Determine winner based on best hand."""
    remaining = [p for p in players if p.active or p.all_in]
    rankings = []

    print("\n--- Showdown ---")
    time.sleep(1)

    for p in remaining:
        combined = p.hand + board
        best = max([HandEvaluator.evaluate_hand(list(c)) 
                    for c in combinations(combined, 5)], 
                    key=lambda x: (HandEvaluator.hand_ranks[x[0]], x[1]))
        rankings.append((p, best))
        print(f"{p.name} hand: {p.hand} | {best[0]}")
        time.sleep(1)

    # Sort by hand strength
    rankings.sort(key=lambda x: (HandEvaluator.hand_ranks[x[1][0]], x[1][1]), reverse=True)
    
    # Check for split pot
    top_hand = rankings[0][1]
    winners = [p for p, hand in rankings if hand == top_hand]
    
    if len(winners) > 1:
        print("\n🤝 Split Pot!")
        return winners, top_hand[0]
    else:
        return [rankings[0][0]], top_hand[0]

# ====== Main Game Loop ======
def play_game():
    players = [
        Player("Bot 1"),
        Player("Bot 2"),
        Player("Bot 3"),
        Player("You", is_human=True)
    ]

    dealer_pos = 0
    small_blind = 500
    big_blind = 1000
    hand_num = 1
    history = []

    while True:
        print(f"\n========== Hand #{hand_num} ==========")
        active_players = [p for p in players if p.chips > 0]
        if len(active_players) < 2:
            print("\n🏆 GAME OVER!")
            winner = active_players[0]
            print(f"🏆 Ultimate Winner: {winner.name} with {winner.chips} chips!")
            break

        if history:
            show_hand_summary(history)

        # Reset players
        for p in players:
            p.reset_for_round()

        deck = Deck()
        board = []
        pot = 0

        # Deal cards
        deal_hands(players, deck)

        # Post blinds
        pot += post_blinds(players, dealer_pos, small_blind, big_blind)

        # ===== Pre-flop =====
        pot, early, winner = betting_round(players, dealer_pos, big_blind, pot, board)
        if early:
            distribute_pot(players, pot, winner)
            log_history(history, hand_num, players, board, pot, winner)
            dealer_pos = (dealer_pos + 1) % len(players)
            hand_num += 1
            input("\nPress Enter for next hand...")
            continue

        # ===== Flop =====
        board.extend(deck.deal(3))
        print("\n💥 FLOP")
        animate_board(board)
        pot, early, winner = betting_round(players, dealer_pos, big_blind, pot, board)
        if early:
            distribute_pot(players, pot, winner)
            log_history(history, hand_num, players, board, pot, winner)
            dealer_pos = (dealer_pos + 1) % len(players)
            hand_num += 1
            input("\nPress Enter for next hand...")
            continue

        # ===== Turn =====
        board.extend(deck.deal(1))
        print("\n🔥 TURN")
        animate_board(board)
        pot, early, winner = betting_round(players, dealer_pos, big_blind, pot, board)
        if early:
            distribute_pot(players, pot, winner)
            log_history(history, hand_num, players, board, pot, winner)
            dealer_pos = (dealer_pos + 1) % len(players)
            hand_num += 1
            input("\nPress Enter for next hand...")
            continue

        # ===== River =====
        board.extend(deck.deal(1))
        print("\n🔥 RIVER")
        animate_board(board)
        pot, early, winner = betting_round(players, dealer_pos, big_blind, pot, board)
        if early:
            distribute_pot(players, pot, winner)
            log_history(history, hand_num, players, board, pot, winner)
            dealer_pos = (dealer_pos + 1) % len(players)
            hand_num += 1
            input("\nPress Enter for next hand...")
            continue

        # ===== Showdown =====
        winners, win_hand = determine_winner(players, board)
        split_pot = pot // len(winners)
        for w in winners:
            distribute_pot(players, split_pot, w)
        log_history(history, hand_num, players, board, pot, winners[0], win_hand)

        dealer_pos = (dealer_pos + 1) % len(players)
        hand_num += 1
        input("\nPress Enter for next hand...")

    # ===== Game Summary =====
    print("\n===== Game Summary =====")
    for entry in history:
        print(f"Hand #{entry['hand']}: Winner - {entry['winner']}, Pot: {entry['pot']}, Board: {entry['board']}, Hand: {entry['winning_hand']}")

# ===== Run the game =====
play_game()
