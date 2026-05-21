from pathlib import Path
import ctypes
import os

import pygame

from blackjack.game import BlackjackEngine


# -----------------------------
# Basic Pygame configuration
# -----------------------------
os.environ["SDL_VIDEO_CENTERED"] = "1"

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except (AttributeError, OSError):
    pass

pygame.init()

WIDTH = 1000
HEIGHT = 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF, vsync=1)
pygame.display.set_caption("Blackjack 21 - Pygame")

CLOCK = pygame.time.Clock()
FPS = 60

# -----------------------------
# Colors
# -----------------------------
GREEN = (25, 120, 70)
DARK_GREEN = (15, 80, 45)
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
RED = (180, 40, 40)
BLUE = (90, 170, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (80, 80, 80)
YELLOW = (235, 200, 80)

# -----------------------------
# Fonts
# -----------------------------
TITLE_FONT = pygame.font.SysFont("bahnschrift", 44, bold=True)
BIG_FONT = pygame.font.SysFont("bahnschrift", 32, bold=True)
FONT = pygame.font.SysFont("bahnschrift", 24)
SMALL_FONT = pygame.font.SysFont("bahnschrift", 16)

# -----------------------------
# Assets
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
CARD_IMAGE_DIR = ASSETS_DIR / "cards"
LOGO_PATH = ASSETS_DIR / "logo.png"

CARD_WIDTH = 112
CARD_HEIGHT = 112
CARD_SPACING = 126
DECK_POSITION = (820, 228)
DEALER_HAND_POSITION = (60, 224)
PLAYER_HAND_POSITION = (60, 440)
CARD_ANIMATION_MS = 260
INSTRUCTIONS_PANEL = pygame.Rect(80, 125, 840, 455)
INSTRUCTIONS_PADDING_X = 35
INSTRUCTIONS_PADDING_Y = 25
INSTRUCTIONS_LINE_HEIGHT = 24
INSTRUCTIONS_SECTION_GAP = 10

card_image_cache = {}

SUIT_TO_FILE = {
    "Hearts": "hearts",
    "Diamonds": "diamonds",
    "Clubs": "clubs",
    "Spades": "spades",
}

INSTRUCTIONS = [
    ("Goal", [
        "Try to get a hand value as close to 21 as possible.",
        "If your total goes over 21, you bust and lose the round.",
    ]),
    ("Card Values", [
        "Cards 2 to 10 are worth their number value.",
        "J, Q and K are each worth 10 points.",
        "A can be worth 1 or 11 automatically.",
    ]),
    ("Player Turn", [
        "Hit draws one more card.",
        "Stand stops drawing and lets the dealer play.",
    ]),
    ("Dealer Rules", [
        "The dealer hits on 16 or lower.",
        "The dealer stands on 17 or higher.",
    ]),
    ("Winning and Chips", [
        "Higher score wins without going over 21.",
        "Equal scores are a Push.",
        "Blackjack beats a regular 21 and pays 1.5x.",
        "A regular win pays 1x your bet.",
        "A loss removes your bet from your chip balance.",
        "A Push returns your bet.",
    ]),
]


def remove_edge_checker_background(image):
    """Make the fake checkerboard background of the logo transparent."""
    image = image.copy().convert_alpha()
    width, height = image.get_size()
    pixels = pygame.PixelArray(image)
    visited = set()
    stack = []

    def is_background_color(color):
        red, green, blue, alpha = image.unmap_rgb(color)
        if alpha == 0:
            return True
        average = (red + green + blue) // 3
        return max(red, green, blue) - min(red, green, blue) <= 14 and average >= 210

    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))

    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))

    transparent = image.map_rgb((255, 255, 255, 0))

    while stack:
        x, y = stack.pop()
        if (x, y) in visited or not (0 <= x < width and 0 <= y < height):
            continue

        visited.add((x, y))

        if not is_background_color(pixels[x, y]):
            continue

        pixels[x, y] = transparent
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    del pixels
    return image


LOGO_IMAGE = pygame.image.load(LOGO_PATH).convert_alpha()
LOGO_IMAGE = remove_edge_checker_background(LOGO_IMAGE)
LOGO_IMAGE = pygame.transform.smoothscale(LOGO_IMAGE, (650, 220))


def get_card_image_path(card):
    """Return the PNG path for a card using the asset pack filename format."""
    suit_name = SUIT_TO_FILE[card.suit]
    rank_name = f"0{card.rank}" if card.rank.isdigit() and int(card.rank) < 10 else card.rank
    return CARD_IMAGE_DIR / f"card_{suit_name}_{rank_name}.png"


def load_card_image(card):
    """Load and cache a card image."""
    path = get_card_image_path(card)

    if path not in card_image_cache:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
        card_image_cache[path] = image

    return card_image_cache[path]


def load_back_card_image():
    """Load and cache the back card image."""
    path = CARD_IMAGE_DIR / "card_back.png"

    if path not in card_image_cache:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
        card_image_cache[path] = image

    return card_image_cache[path]


class Button:
    """Simple clickable button for the Pygame interface."""

    def __init__(self, x, y, width, height, text, color=DARK_GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def is_hovered(self):
        """Return True when the mouse is currently over the button."""
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, surface):
        """Draw the button."""
        hovered = self.is_hovered()
        color = tuple(min(255, channel + 28) for channel in self.color) if hovered else self.color
        border_width = 3 if hovered else 2
        y_offset = -2 if hovered else 0
        draw_rect = self.rect.move(0, y_offset)

        if hovered:
            shadow_rect = self.rect.move(0, 4)
            pygame.draw.rect(surface, (10, 55, 32), shadow_rect, border_radius=10)

        pygame.draw.rect(surface, color, draw_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, draw_rect, border_width, border_radius=10)

        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, event):
        """Return True if the button was clicked."""
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


def draw_text(surface, text, font, color, x, y):
    """Draw text on screen."""
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


def draw_wrapped_text(surface, text, font, color, x, y, max_width, line_height):
    """Draw text wrapped by actual pixel width."""
    for line in wrap_text(text, font, max_width):
        draw_text(surface, line, font, color, x, y)
        y += line_height


def get_status_message_color(message):
    """Choose a result color for the current status message."""
    lower_message = message.lower()

    if "lose" in lower_message or "busted" in lower_message or "dealer has blackjack" in lower_message:
        return RED
    if "win" in lower_message or "blackjack!" in lower_message or "gain" in lower_message:
        return BLUE

    return WHITE


def draw_card(surface, card, x, y, hidden=False):
    """Draw a visible card or the card back."""
    image = load_back_card_image() if hidden else load_card_image(card)
    surface.blit(image, (x, y))


def draw_hand(surface, cards, x, y, hidden_second_card=False):
    """Draw all cards from a hand."""
    for index, card in enumerate(cards):
        hidden = hidden_second_card and index == 1
        draw_card(surface, card, x + index * CARD_SPACING, y, hidden)


def get_card_position(owner, index):
    """Return the final table position for an animated card."""
    if owner == "dealer":
        x, y = DEALER_HAND_POSITION
    else:
        x, y = PLAYER_HAND_POSITION

    return x + index * CARD_SPACING, y


def queue_card_animation(animations, owner, index, hidden=False, delay_ms=0):
    """Add one moving card animation from the deck to a hand."""
    animations.append({
        "owner": owner,
        "index": index,
        "hidden": hidden,
        "start": DECK_POSITION,
        "end": get_card_position(owner, index),
        "start_time": pygame.time.get_ticks() + delay_ms,
        "duration": CARD_ANIMATION_MS,
    })


def queue_initial_deal_animations(animations):
    """Animate the opening deal in player/dealer/player/dealer order."""
    animations.clear()
    delay = 0
    for owner, index, hidden in (
        ("player", 0, False),
        ("dealer", 0, False),
        ("player", 1, False),
        ("dealer", 1, True),
    ):
        queue_card_animation(animations, owner, index, hidden, delay)
        delay += 120


def update_card_animations(animations, visible_counts):
    """Advance animations and reveal cards once they reach their hand."""
    now = pygame.time.get_ticks()

    for animation in animations[:]:
        if now < animation["start_time"] + animation["duration"]:
            continue

        owner = animation["owner"]
        visible_counts[owner] = max(visible_counts[owner], animation["index"] + 1)
        animations.remove(animation)


def draw_card_animations(surface, animations, state):
    """Draw any card currently flying from the deck to a hand."""
    now = pygame.time.get_ticks()

    for animation in animations:
        if now < animation["start_time"]:
            continue

        progress = min(1, (now - animation["start_time"]) / animation["duration"])
        eased = 1 - (1 - progress) ** 3
        start_x, start_y = animation["start"]
        end_x, end_y = animation["end"]
        x = start_x + (end_x - start_x) * eased
        y = start_y + (end_y - start_y) * eased
        owner = animation["owner"]
        cards = state["dealer_cards"] if owner == "dealer" else state["player_cards"]

        if animation["hidden"]:
            image = load_back_card_image()
        elif animation["index"] < len(cards):
            image = load_card_image(cards[animation["index"]])
        else:
            image = load_back_card_image()

        surface.blit(image, (round(x), round(y)))


def draw_menu(surface, buttons):
    """Draw the main menu screen only."""
    play_button, instructions_button, exit_menu_button = buttons

    surface.fill(GREEN)
    pygame.draw.rect(surface, DARK_GREEN, (0, 0, WIDTH, 160))

    logo_rect = LOGO_IMAGE.get_rect(center=(WIDTH // 2, 160))
    surface.blit(LOGO_IMAGE, logo_rect)

    subtitle = FONT.render("Choose an option to start", True, WHITE)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 290))
    surface.blit(subtitle, subtitle_rect)

    play_button.draw(surface)
    instructions_button.draw(surface)
    exit_menu_button.draw(surface)


def wrap_text(text, font, max_width):
    """Split text into lines that fit within max_width."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        candidate = word if not current_line else f"{current_line} {word}"
        if font.size(candidate)[0] <= max_width:
            current_line = candidate
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines or [""]


def get_instructions_content_height():
    """Return the full height needed by the instructions text."""
    height = INSTRUCTIONS_PADDING_Y
    max_line_width = INSTRUCTIONS_PANEL.width - INSTRUCTIONS_PADDING_X * 2 - 60

    for _, lines in INSTRUCTIONS:
        height += 30
        for line in lines:
            height += len(wrap_text(line, SMALL_FONT, max_line_width)) * INSTRUCTIONS_LINE_HEIGHT
        height += INSTRUCTIONS_SECTION_GAP

    return height + INSTRUCTIONS_PADDING_Y


def get_max_instruction_scroll():
    """Return the largest valid scroll offset for the instructions panel."""
    content_height = get_instructions_content_height()
    return max(0, content_height - INSTRUCTIONS_PANEL.height)


def clamp_instruction_scroll(scroll_offset):
    """Keep instruction scrolling inside its valid range."""
    return max(0, min(get_max_instruction_scroll(), scroll_offset))


def draw_instructions(surface, back_button, scroll_offset):
    """Draw the instructions screen only."""
    surface.fill(GREEN)
    pygame.draw.rect(surface, DARK_GREEN, (0, 0, WIDTH, 100))

    title = TITLE_FONT.render("How to Play Blackjack", True, YELLOW)
    title_rect = title.get_rect(center=(WIDTH // 2, 50))
    surface.blit(title, title_rect)

    pygame.draw.rect(surface, DARK_GREEN, INSTRUCTIONS_PANEL, border_radius=18)
    pygame.draw.rect(surface, WHITE, INSTRUCTIONS_PANEL, 2, border_radius=18)

    content_height = get_instructions_content_height()
    content = pygame.Surface((INSTRUCTIONS_PANEL.width - 24, content_height), pygame.SRCALPHA)

    x = INSTRUCTIONS_PADDING_X
    y = INSTRUCTIONS_PADDING_Y
    max_line_width = INSTRUCTIONS_PANEL.width - INSTRUCTIONS_PADDING_X * 2 - 60

    for section_title, lines in INSTRUCTIONS:
        section_surface = FONT.render(section_title, True, YELLOW)
        content.blit(section_surface, (x, y))
        y += 30

        for line in lines:
            wrapped_lines = wrap_text(line, SMALL_FONT, max_line_width)
            for index, wrapped_line in enumerate(wrapped_lines):
                prefix = "- " if index == 0 else "  "
                line_surface = SMALL_FONT.render(f"{prefix}{wrapped_line}", True, WHITE)
                content.blit(line_surface, (x + 25, y))
                y += INSTRUCTIONS_LINE_HEIGHT

        y += INSTRUCTIONS_SECTION_GAP

    scroll_offset = clamp_instruction_scroll(scroll_offset)
    visible_area = pygame.Rect(0, scroll_offset, content.get_width(), INSTRUCTIONS_PANEL.height - 4)
    surface.blit(content, (INSTRUCTIONS_PANEL.x + 2, INSTRUCTIONS_PANEL.y + 2), visible_area)

    max_scroll = get_max_instruction_scroll()
    if max_scroll > 0:
        track_rect = pygame.Rect(INSTRUCTIONS_PANEL.right - 16, INSTRUCTIONS_PANEL.y + 12, 6, INSTRUCTIONS_PANEL.height - 24)
        thumb_height = max(45, int(track_rect.height * INSTRUCTIONS_PANEL.height / content_height))
        thumb_range = track_rect.height - thumb_height
        thumb_y = track_rect.y + int((scroll_offset / max_scroll) * thumb_range)
        thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_height)

        pygame.draw.rect(surface, (70, 145, 95), track_rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, thumb_rect, border_radius=4)

    back_button.draw(surface)


def draw_game_screen(surface, state, current_bet, buttons, visible_counts, animations):
    """Draw the Blackjack table screen only."""
    (
        minus_50_button,
        minus_10_button,
        plus_10_button,
        plus_50_button,
        deal_button,
        next_round_button,
        hit_button,
        stand_button,
        menu_button,
    ) = buttons

    surface.fill(GREEN)
    pygame.draw.rect(surface, DARK_GREEN, (0, 0, WIDTH, 92))
    draw_text(surface, "Blackjack 21", TITLE_FONT, WHITE, 32, 20)
    draw_text(surface, "Chips", SMALL_FONT, GRAY, 790, 20)
    draw_text(surface, f"{state['chips']}", BIG_FONT, YELLOW, 790, 42)

    status_rect = pygame.Rect(60, 110, 880, 46)
    pygame.draw.rect(surface, (18, 95, 55), status_rect, border_radius=10)
    pygame.draw.rect(surface, (70, 145, 95), status_rect, 2, border_radius=10)
    draw_text(surface, "Status", SMALL_FONT, GRAY, status_rect.x + 18, status_rect.y + 8)
    draw_wrapped_text(
        surface,
        state["message"],
        SMALL_FONT,
        get_status_message_color(state["message"]),
        status_rect.x + 92,
        status_rect.y + 8,
        status_rect.width - 115,
        20,
    )

    draw_text(surface, "Dealer", BIG_FONT, WHITE, 60, 158)
    if state["dealer_score"] is None and state["dealer_visible_score"] is not None:
        draw_text(surface, f"Visible score: {state['dealer_visible_score']}", FONT, WHITE, 60, 194)
    elif state["dealer_score"] is not None:
        draw_text(surface, f"Score: {state['dealer_score']}", FONT, WHITE, 60, 194)
    pygame.draw.rect(surface, (18, 95, 55), (*DECK_POSITION, CARD_WIDTH, CARD_HEIGHT), border_radius=8)
    pygame.draw.rect(surface, (70, 145, 95), (*DECK_POSITION, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=8)
    draw_card(surface, None, DECK_POSITION[0], DECK_POSITION[1], hidden=True)

    dealer_cards = state["dealer_cards"][:visible_counts["dealer"]]
    draw_hand(surface, dealer_cards, *DEALER_HAND_POSITION, hidden_second_card=state["dealer_hidden"])

    draw_text(surface, "Player", BIG_FONT, WHITE, 60, 378)
    draw_text(surface, f"Score: {state['player_score']}", FONT, WHITE, 60, 414)
    player_cards = state["player_cards"][:visible_counts["player"]]
    draw_hand(surface, player_cards, *PLAYER_HAND_POSITION)
    draw_card_animations(surface, animations, state)

    control_bar = pygame.Rect(0, 600, WIDTH, 100)
    pygame.draw.rect(surface, (18, 95, 55), control_bar)
    pygame.draw.line(surface, (45, 150, 85), (0, control_bar.y), (WIDTH, control_bar.y), 3)

    bet_panel = pygame.Rect(32, 612, 640, 74)
    action_panel = pygame.Rect(690, 612, 280, 74)
    pygame.draw.rect(surface, DARK_GREEN, bet_panel, border_radius=14)
    pygame.draw.rect(surface, DARK_GREEN, action_panel, border_radius=14)

    draw_text(surface, "Current Bet", SMALL_FONT, GRAY, 58, 620)
    draw_text(surface, str(current_bet), BIG_FONT, WHITE, 58, 641)
    helper_text = "Round in progress" if state["round_active"] else "Adjust bet, then press Deal"
    helper_color = YELLOW if state["round_active"] else GRAY
    draw_text(surface, helper_text, SMALL_FONT, helper_color, 205, 620)
    draw_text(surface, "Actions", SMALL_FONT, GRAY, 714, 620)

    minus_50_button.draw(surface)
    minus_10_button.draw(surface)
    plus_10_button.draw(surface)
    plus_50_button.draw(surface)
    if state["round_over"] and not state["game_over"]:
        next_round_button.draw(surface)
    else:
        deal_button.draw(surface)
    hit_button.draw(surface)
    stand_button.draw(surface)
    menu_button.draw(surface)

    if state["game_over"]:
        pygame.draw.rect(surface, BLACK, (250, 260, 500, 150), border_radius=20)
        pygame.draw.rect(surface, WHITE, (250, 260, 500, 150), 3, border_radius=20)
        draw_text(surface, "GAME OVER", TITLE_FONT, RED, 370, 285)
        draw_text(surface, "You have 0 chips.", FONT, WHITE, 390, 350)


def update_cursor(screen_state, state, buttons, animations_running):
    """Use a hand cursor when hovering over an available button."""
    mouse_position = pygame.mouse.get_pos()
    active_buttons = []

    if screen_state == "menu":
        active_buttons = [buttons["play"], buttons["instructions"], buttons["exit"]]
    elif screen_state == "instructions":
        active_buttons = [buttons["back"]]
    elif screen_state == "game" and not animations_running:
        active_buttons = [buttons["hit"], buttons["stand"], buttons["menu"]]

        if not state["round_active"]:
            active_buttons.extend((
                buttons["minus_50"],
                buttons["minus_10"],
                buttons["plus_10"],
                buttons["plus_50"],
            ))

        if state["round_over"] and not state["game_over"]:
            active_buttons.append(buttons["next"])
        elif not state["round_active"] and not state["game_over"]:
            active_buttons.append(buttons["deal"])

        if state["round_active"]:
            active_buttons.extend((buttons["hit"], buttons["stand"]))

    cursor = pygame.SYSTEM_CURSOR_ARROW
    if any(button.rect.collidepoint(mouse_position) for button in active_buttons):
        cursor = pygame.SYSTEM_CURSOR_HAND

    pygame.mouse.set_cursor(cursor)


def main():
    """Main Pygame loop."""
    game = BlackjackEngine()
    current_bet = 100
    screen_state = "menu"
    instruction_scroll = 0
    instruction_dragging = False
    last_drag_y = 0
    visible_counts = {"player": 0, "dealer": 0}
    card_animations = []

    play_button = Button(400, 350, 200, 60, "Play", (40, 120, 180))
    instructions_button = Button(350, 440, 300, 60, "Instructions", (80, 80, 160))
    exit_menu_button = Button(400, 530, 200, 60, "Exit", (150, 50, 50))
    back_button = Button(40, 610, 160, 50, "Back", (90, 90, 90))
    minus_50_button = Button(205, 642, 72, 36, "-50")
    minus_10_button = Button(287, 642, 72, 36, "-10")
    plus_10_button = Button(369, 642, 72, 36, "+10")
    plus_50_button = Button(451, 642, 72, 36, "+50")
    deal_button = Button(535, 642, 112, 36, "Deal", (40, 120, 180))
    next_round_button = Button(535, 642, 112, 36, "Next", (40, 120, 180))
    hit_button = Button(704, 642, 70, 36, "Hit", (40, 140, 80))
    stand_button = Button(784, 642, 84, 36, "Stand", (160, 100, 40))
    menu_button = Button(878, 642, 78, 36, "Menu", (150, 50, 50))
    buttons = {
        "play": play_button,
        "instructions": instructions_button,
        "exit": exit_menu_button,
        "back": back_button,
        "minus_50": minus_50_button,
        "minus_10": minus_10_button,
        "plus_10": plus_10_button,
        "plus_50": plus_50_button,
        "deal": deal_button,
        "next": next_round_button,
        "hit": hit_button,
        "stand": stand_button,
        "menu": menu_button,
    }

    running = True

    while running:
        CLOCK.tick(FPS)
        state = game.get_state()
        update_card_animations(card_animations, visible_counts)
        animations_running = bool(card_animations)
        update_cursor(screen_state, state, buttons, animations_running)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if screen_state == "menu":
                if play_button.is_clicked(event):
                    screen_state = "game"
                elif instructions_button.is_clicked(event):
                    screen_state = "instructions"
                    instruction_scroll = 0
                elif exit_menu_button.is_clicked(event):
                    running = False

            elif screen_state == "instructions":
                if back_button.is_clicked(event):
                    screen_state = "menu"
                    instruction_dragging = False

                elif event.type == pygame.MOUSEWHEEL:
                    instruction_scroll = clamp_instruction_scroll(instruction_scroll - event.y * 35)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if INSTRUCTIONS_PANEL.collidepoint(event.pos):
                        instruction_dragging = True
                        last_drag_y = event.pos[1]

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    instruction_dragging = False

                elif event.type == pygame.MOUSEMOTION and instruction_dragging:
                    current_y = event.pos[1]
                    instruction_scroll = clamp_instruction_scroll(instruction_scroll + last_drag_y - current_y)
                    last_drag_y = current_y

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        instruction_scroll = clamp_instruction_scroll(instruction_scroll + 35)
                    elif event.key == pygame.K_UP:
                        instruction_scroll = clamp_instruction_scroll(instruction_scroll - 35)
                    elif event.key == pygame.K_PAGEDOWN:
                        instruction_scroll = clamp_instruction_scroll(instruction_scroll + 180)
                    elif event.key == pygame.K_PAGEUP:
                        instruction_scroll = clamp_instruction_scroll(instruction_scroll - 180)

            elif screen_state == "game":
                if animations_running:
                    continue

                if minus_50_button.is_clicked(event) and not state["round_active"]:
                    current_bet = max(10, current_bet - 50)
                elif minus_10_button.is_clicked(event) and not state["round_active"]:
                    current_bet = max(10, current_bet - 10)
                elif plus_10_button.is_clicked(event) and not state["round_active"]:
                    current_bet = min(state["chips"], current_bet + 10)
                elif plus_50_button.is_clicked(event) and not state["round_active"]:
                    current_bet = min(state["chips"], current_bet + 50)
                elif (
                    deal_button.is_clicked(event)
                    and not state["round_active"]
                    and not state["round_over"]
                    and not state["game_over"]
                ):
                    current_bet = min(current_bet, state["chips"])
                    if game.start_round(current_bet):
                        visible_counts = {"player": 0, "dealer": 0}
                        queue_initial_deal_animations(card_animations)
                elif next_round_button.is_clicked(event) and state["round_over"] and not state["game_over"]:
                    current_bet = min(current_bet, state["chips"])
                    if game.start_round(current_bet):
                        visible_counts = {"player": 0, "dealer": 0}
                        queue_initial_deal_animations(card_animations)
                elif hit_button.is_clicked(event) and state["round_active"]:
                    previous_count = len(state["player_cards"])
                    game.hit()
                    new_state = game.get_state()
                    if len(new_state["player_cards"]) > previous_count:
                        queue_card_animation(card_animations, "player", len(new_state["player_cards"]) - 1)
                elif stand_button.is_clicked(event) and state["round_active"]:
                    previous_count = len(state["dealer_cards"])
                    game.stand()
                    new_state = game.get_state()
                    visible_counts["dealer"] = min(previous_count, len(new_state["dealer_cards"]))
                    for index in range(previous_count, len(new_state["dealer_cards"])):
                        queue_card_animation(card_animations, "dealer", index, delay_ms=(index - previous_count) * 120)
                elif menu_button.is_clicked(event):
                    screen_state = "menu"

        state = game.get_state()

        if screen_state == "menu":
            draw_menu(SCREEN, (play_button, instructions_button, exit_menu_button))
        elif screen_state == "instructions":
            draw_instructions(SCREEN, back_button, instruction_scroll)
        elif screen_state == "game":
            draw_game_screen(
                SCREEN,
                state,
                current_bet,
                (
                    minus_50_button,
                    minus_10_button,
                    plus_10_button,
                    plus_50_button,
                    deal_button,
                    next_round_button,
                    hit_button,
                    stand_button,
                    menu_button,
                ),
                visible_counts,
                card_animations,
            )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
