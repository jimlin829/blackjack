from blackjack.cards import Card, Deck


STARTING_CHIPS = 1000
DEALER_STAND_SCORE = 17
BLACKJACK_SCORE = 21


class Hand:
    """Cards held by either the player or the dealer."""

    def __init__(self) -> None:
        self.cards: list[Card] = []

    def add(self, card: Card) -> None:
        """Add a newly drawn card to the hand."""
        self.cards.append(card)

    @property
    def score(self) -> int:
        """Calculate the best Blackjack score for this hand.

        Aces are counted as 11 first. If the hand would bust, each ace can be
        reduced from 11 to 1 by subtracting 10 until the total is safe or there
        are no more aces to adjust.
        """
        total = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == "A")

        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    @property
    def is_busted(self) -> bool:
        """Return True when the hand is over 21."""
        return self.score > BLACKJACK_SCORE

    @property
    def is_blackjack(self) -> bool:
        """Return True for a natural Blackjack: exactly two cards worth 21."""
        return len(self.cards) == 2 and self.score == BLACKJACK_SCORE

    def visible(self) -> str:
        """Show all cards in this hand as readable text."""
        return ", ".join(str(card) for card in self.cards)

    def display(self, owner: str) -> str:
        """Return a complete hand display with cards and current total."""
        return f"{owner}: {self.visible()} | Total: {self.score}"

    def display_with_hidden_card(self, owner: str) -> str:
        """Return the dealer hand display while one card is still face-down."""
        if not self.cards:
            return f"{owner}: No cards"
        return f"{owner}: {self.cards[0]}, [Hidden card] | Visible total: {self.cards[0].value}"


class Game:
    """Console Blackjack game with chip betting and replay support."""

    def __init__(self) -> None:
        self.chips = STARTING_CHIPS

    def run(self) -> None:
        """Run rounds until the player quits or runs out of chips."""
        print("=" * 46)
        print("Welcome to Blackjack 21")
        print("=" * 46)

        while self.chips > 0:
            print(f"\nCurrent chip balance: {self.chips}")
            bet = self._ask_for_bet()
            result = self._play_round(bet)
            self._settle_bet(result, bet)
            print(f"Chip balance after round: {self.chips}")

            if self.chips <= 0:
                print("\nYou have 0 chips. Game over.")
                return

            if not self._ask_yes_no("\nPlay another round? Enter 'y' for yes or 'n' for no: "):
                print(f"\nThanks for playing. Final chip balance: {self.chips}")
                return

        print("\nYou have 0 chips. Game over.")

    def _play_round(self, bet: int) -> str:
        """Play one full round and return the outcome keyword."""
        deck = Deck()
        player = Hand()
        dealer = Hand()

        self._deal_initial_cards(deck, player, dealer)
        print("\nInitial deal:")
        self._show_table(player, dealer, hide_dealer_card=True)

        # Natural Blackjack is checked before normal turns. A natural Blackjack
        # beats a regular 21, and two natural Blackjacks push.
        if player.is_blackjack or dealer.is_blackjack:
            return self._resolve_initial_blackjack(player, dealer)

        if self._player_turn(deck, player, dealer) == "player_bust":
            self._show_table(player, dealer, hide_dealer_card=False)
            print("\nYou busted. Dealer wins.")
            return "loss"

        self._dealer_turn(deck, dealer)
        self._show_table(player, dealer, hide_dealer_card=False)
        return self._compare_hands(player, dealer)

    def _deal_initial_cards(self, deck: Deck, player: Hand, dealer: Hand) -> None:
        """Deal two cards each, alternating between player and dealer."""
        for _ in range(2):
            player.add(deck.draw())
            dealer.add(deck.draw())

    def _player_turn(self, deck: Deck, player: Hand, dealer: Hand) -> str:
        """Handle the player's hit/stand decisions with input validation."""
        while True:
            print("\nYour turn:")
            self._show_table(player, dealer, hide_dealer_card=True)

            choice = self._ask_hit_or_stand()
            if choice == "s":
                print("You stand.")
                return "stand"

            card = deck.draw()
            player.add(card)
            print(f"You hit and drew: {card}")

            if player.is_busted:
                return "player_bust"

    def _dealer_turn(self, deck: Deck, dealer: Hand) -> None:
        """Dealer hits on 16 or below and stands on 17 or above."""
        print("\nDealer's turn:")
        while dealer.score < DEALER_STAND_SCORE:
            card = deck.draw()
            dealer.add(card)
            print(f"Dealer hits and draws: {card} | Dealer total: {dealer.score}")

        print(f"Dealer stands with total: {dealer.score}")

    def _resolve_initial_blackjack(self, player: Hand, dealer: Hand) -> str:
        """Resolve the round immediately if either side has Blackjack."""
        print("\nBlackjack check:")
        self._show_table(player, dealer, hide_dealer_card=False)

        if player.is_blackjack and dealer.is_blackjack:
            print("Both player and dealer have Blackjack. Push.")
            return "push"
        if player.is_blackjack:
            print("Blackjack! You win with a natural 21.")
            return "blackjack"

        print("Dealer has Blackjack. You lose.")
        return "loss"

    def _compare_hands(self, player: Hand, dealer: Hand) -> str:
        """Compare final totals and return win, loss, or push."""
        if dealer.is_busted:
            print("\nDealer busted. You win.")
            return "win"
        if player.score > dealer.score:
            print("\nYour total is higher. You win.")
            return "win"
        if player.score < dealer.score:
            print("\nDealer's total is higher. You lose.")
            return "loss"

        print("\nEqual totals. Push.")
        return "push"

    def _settle_bet(self, result: str, bet: int) -> None:
        """Apply the chip payout for the round outcome."""
        if result == "blackjack":
            payout = int(bet * 1.5)
            self.chips += payout
            print(f"Blackjack pays 1.5x. You gain {payout} chips.")
        elif result == "win":
            self.chips += bet
            print(f"Regular win pays 1x. You gain {bet} chips.")
        elif result == "loss":
            self.chips -= bet
            print(f"You lose your bet of {bet} chips.")
        else:
            print("Push. Your bet is returned.")

    def _show_table(self, player: Hand, dealer: Hand, hide_dealer_card: bool) -> None:
        """Display the current visible table state."""
        print(player.display("Player"))
        if hide_dealer_card:
            print(dealer.display_with_hidden_card("Dealer"))
        else:
            print(dealer.display("Dealer"))

    def _ask_for_bet(self) -> int:
        """Prompt until the player enters a valid bet within their balance."""
        while True:
            raw_bet = input(f"Place your bet, from 1 to {self.chips}: ").strip()

            if not raw_bet.isdigit():
                print("Invalid bet. Please enter a whole number.")
                continue

            bet = int(raw_bet)
            if bet < 1:
                print("Invalid bet. The minimum bet is 1 chip.")
                continue
            if bet > self.chips:
                print("Invalid bet. You cannot bet more chips than you have.")
                continue

            return bet

    def _ask_hit_or_stand(self) -> str:
        """Prompt until the player chooses hit or stand."""
        while True:
            choice = input("Choose your action: enter 'h' to hit or 's' to stand: ").strip().lower()
            if choice in {"h", "s"}:
                return choice
            print("Invalid command. Please enter only 'h' or 's'.")

    def _ask_yes_no(self, prompt: str) -> bool:
        """Prompt until the player answers yes or no."""
        while True:
            choice = input(prompt).strip().lower()
            if choice == "y":
                return True
            if choice == "n":
                return False
            print("Invalid command. Please enter only 'y' or 'n'.")


class BlackjackEngine:
    """Game engine for the Pygame version.

    This class contains only the Blackjack logic.
    """

    def __init__(self) -> None:
        self.chips = STARTING_CHIPS
        self.deck: Deck | None = None
        self.player: Hand | None = None
        self.dealer: Hand | None = None
        self.bet = 0
        self.message = "Place a bet and start a new round."
        self.round_active = False
        self.round_over = False
        self.dealer_hidden = True

    def start_round(self, bet: int) -> bool:
        """Start a new round if the bet is valid."""
        if self.chips <= 0:
            self.message = "You have 0 chips. Game over."
            return False

        if bet < 1:
            self.message = "Bet must be at least 1 chip."
            return False

        if bet > self.chips:
            self.message = "You cannot bet more chips than you have."
            return False

        self.bet = bet
        self.deck = Deck()
        self.player = Hand()
        self.dealer = Hand()

        for _ in range(2):
            self.player.add(self.deck.draw())
            self.dealer.add(self.deck.draw())

        self.round_active = True
        self.round_over = False
        self.dealer_hidden = True
        self.message = "Your turn: Hit or Stand."

        # Check natural Blackjack immediately.
        if self.player.is_blackjack or self.dealer.is_blackjack:
            self.dealer_hidden = False
            self.round_active = False
            self.round_over = True

            if self.player.is_blackjack and self.dealer.is_blackjack:
                self.message = "Both have Blackjack. Push."
            elif self.player.is_blackjack:
                payout = int(self.bet * 1.5)
                self.chips += payout
                self.message = f"Blackjack! You gain {payout} chips."
            else:
                self.chips -= self.bet
                self.message = "Dealer has Blackjack. You lose."

        return True

    def hit(self) -> None:
        """Player draws one card."""
        if not self.round_active or self.player is None or self.deck is None:
            return

        card = self.deck.draw()
        self.player.add(card)

        if self.player.is_busted:
            self.dealer_hidden = False
            self.round_active = False
            self.round_over = True
            self.chips -= self.bet
            self.message = f"You drew {card}. You busted. You lose {self.bet} chips."
        elif self.player.score == BLACKJACK_SCORE:
            self.message = f"You drew {card}. You reached 21."
            self.stand()
        else:
            self.message = f"You drew {card}. Hit or Stand?"

    def stand(self) -> None:
        """Player stands. Dealer plays automatically."""
        if not self.round_active or self.dealer is None or self.deck is None:
            return

        self.dealer_hidden = False

        while self.dealer.score < DEALER_STAND_SCORE:
            self.dealer.add(self.deck.draw())

        self.round_active = False
        self.round_over = True
        self._resolve_round()

    def _resolve_round(self) -> None:
        """Compare player and dealer hands and update chips."""
        if self.player is None or self.dealer is None:
            return

        if self.dealer.is_busted:
            self.chips += self.bet
            self.message = f"Dealer busted. You win {self.bet} chips."
        elif self.player.score > self.dealer.score:
            self.chips += self.bet
            self.message = f"You win {self.bet} chips."
        elif self.player.score < self.dealer.score:
            self.chips -= self.bet
            self.message = f"You lose {self.bet} chips."
        else:
            self.message = "Push. Your bet is returned."

    def get_state(self) -> dict:
        """Return all data needed by the interface."""
        return {
            "chips": self.chips,
            "bet": self.bet,
            "player_cards": self.player.cards if self.player else [],
            "dealer_cards": self.dealer.cards if self.dealer else [],
            "player_score": self.player.score if self.player else 0,
            "dealer_score": self.dealer.score if self.dealer and not self.dealer_hidden else None,
            "dealer_visible_score": self.dealer.cards[0].value if self.dealer and self.dealer_hidden else None,
            "dealer_hidden": self.dealer_hidden,
            "message": self.message,
            "round_active": self.round_active,
            "round_over": self.round_over,
            "game_over": self.chips <= 0,
        }
