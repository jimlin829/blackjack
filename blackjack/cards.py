from dataclasses import dataclass
from random import shuffle


SUITS = ("Hearts", "Diamonds", "Clubs", "Spades")
RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")


@dataclass(frozen=True)
class Card:
    """A single playing card from a standard 52-card deck."""

    rank: str
    suit: str

    @property
    def value(self) -> int:
        """Return the base Blackjack value for this card.

        Aces start at 11 here. The Hand class later adjusts aces down to 1
        whenever that is needed to avoid busting.
        """
        if self.rank == "A":
            return 11
        if self.rank in {"J", "Q", "K"}:
            return 10
        return int(self.rank)

    def __str__(self) -> str:
        return f"{self.rank} of {self.suit}"


class Deck:
    """A shuffled standard 52-card deck with no jokers."""

    def __init__(self) -> None:
        # Create every rank/suit combination and shuffle immediately so each
        # round starts with a fresh random deck.
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        shuffle(self.cards)

    def draw(self) -> Card:
        """Draw one card from the top of the deck."""
        if not self.cards:
            raise RuntimeError("The deck is empty.")
        return self.cards.pop()
