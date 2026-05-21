# Blackjack 21 - Python / Pygame
<p align="center">
  <img src="blackjack/assets/logo1.png" alt="Blackjack 21 screenshot" width="700">
</p>

Blackjack 21 is a desktop card game built with Python and Pygame. It includes a graphical interface, chip betting, dealer logic, card animations, hover effects, and full Blackjack rules.

There is also a browser-playable version available from my portfolio:

[Play online](https://www.yhlinworks.com/projects/blackjack/)

## Features

- Standard 52-card deck with automatic shuffling.
- Player and dealer hands with visual card display.
- Dealer has one hidden card during the player's turn.
- Correct Blackjack scoring:
  - Number cards use face value.
  - J, Q and K count as 10.
  - Aces count as 1 or 11 automatically.
- Natural Blackjack detection.
- Dealer hits on 16 or below and stands on 17 or above.
- Chip system starting at 1000 chips.
- Bet controls: `-50`, `-10`, `+10`, `+50`.
- Blackjack payout: 1.5x the bet.
- Regular win payout: 1x the bet.
- Push returns the bet.
- Card dealing animations.
- Hover effects and hand cursor on buttons.
- Instructions screen with scrollable content.
- Game over when chips reach 0.

## Screens

- Main menu
- Instructions
- Blackjack table
- Betting controls
- Dealer and player turns
- Round result messages

## Requirements

- Python 3.11 or newer
- Pygame 2.6 or newer

## Installation

Clone the repository:

```powershell
git clone https://github.com/jimlin829/blackjack.git
cd blackjack
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\activate
```

Install the project:

```powershell
pip install -e .
```

For development and tests:

```powershell
pip install -e ".[dev]"
```

## Run the Game

```powershell
python -m blackjack
```

Or, after installing the package:

```powershell
blackjack
```

## Project Structure

```text
BJ/
|-- blackjack/
|   |-- assets/
|   |   |-- cards/
|   |   `-- logo.png
|   |-- cards.py
|   |-- cli.py
|   |-- game.py
|   |-- gui.py
|   |-- __init__.py
|   `-- __main__.py
|-- .gitignore
|-- pyproject.toml
`-- README.md
```

## Main Files

- `blackjack/cards.py`: Card and Deck classes.
- `blackjack/game.py`: Blackjack rules, hand scoring, betting, and game engine.
- `blackjack/gui.py`: Pygame graphical interface.
- `blackjack/cli.py`: Console entry point kept for compatibility.

## Game Rules

1. The game uses one standard 52-card deck.
2. The player and dealer receive two cards.
3. The player sees both cards.
4. The dealer shows one card and hides the second card.
5. The player can Hit or Stand.
6. If the player goes over 21, the player loses immediately.
7. If the player reaches 21, the dealer turn starts automatically.
8. The dealer hits on 16 or below.
9. The dealer stands on 17 or above.
10. Higher score wins if neither side busts.
11. Equal scores result in a Push.
12. Natural Blackjack beats a regular 21.

## Notes for GitHub

Do not commit the virtual environment folder:

```text
.venv/
```

The `.gitignore` file already excludes common Python cache files, virtual environments, and build outputs.

## Technologies

- Python
- Pygame
- Pytest
- HTML, CSS and JavaScript for the online portfolio demo

## Author

YanHao Lin

- Portfolio: [www.yhlinworks.com](https://www.yhlinworks.com)
- GitHub: [jimlin829](https://github.com/jimlin829)
