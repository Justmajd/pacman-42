import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.contracts import GameState  # noqa: E402
from src.ui.menu import Menu  # noqa: E402
from src.ui.screens import (  # noqa: E402
    GameOverScreen,
    InstructionsScreen,
    MainMenuScreen,
    PauseScreen,
    VictoryScreen,
)

pygame.init()
pygame.font.init()


def key_event(key: int, unicode: str = "") -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode)


def type_text(screen: object, text: str) -> None:
    for char in text:
        key = getattr(pygame, f"K_{char.lower()}")
        screen.handle_event(key_event(key, unicode=char.lower()))


# --- Menu widget -----------------------------------------------------------

def test_menu_move_down_clamped_at_last_option() -> None:
    menu = Menu(options=["A", "B", "C"])

    menu.move_down()
    menu.move_down()
    menu.move_down()
    menu.move_down()

    assert menu.selected_index == 2


def test_menu_move_up_clamped_at_first_option() -> None:
    menu = Menu(options=["A", "B", "C"])

    menu.move_up()
    menu.move_up()

    assert menu.selected_index == 0


def test_menu_selected_option_tracks_index() -> None:
    menu = Menu(options=["Start", "Exit"])

    assert menu.selected_option() == "Start"
    menu.move_down()
    assert menu.selected_option() == "Exit"


# --- MainMenuScreen ----------------------------------------------------------

def test_main_menu_ignores_non_keydown_events() -> None:
    screen = MainMenuScreen(
        menu=Menu(options=["Start", "Highscores", "Instructions", "Exit"])
    )

    result = screen.handle_event(pygame.event.Event(pygame.MOUSEMOTION))

    assert result is None


def test_main_menu_navigation_reaches_every_option() -> None:
    screen = MainMenuScreen(
        menu=Menu(options=["Start", "Highscores", "Instructions", "Exit"])
    )

    expected = [
        (0, GameState.PLAYING),
        (1, GameState.HIGHSCORES),
        (2, GameState.INSTRUCTIONS),
        (3, GameState.EXIT),
    ]
    for target_index, expected_state in expected:
        screen.menu.selected_index = target_index
        result = screen.handle_event(key_event(pygame.K_RETURN))
        assert result == expected_state


def test_main_menu_down_key_moves_selection() -> None:
    screen = MainMenuScreen(
        menu=Menu(options=["Start", "Highscores", "Instructions", "Exit"])
    )

    screen.handle_event(key_event(pygame.K_DOWN))

    assert screen.menu.selected_index == 1


# --- PauseScreen -------------------------------------------------------------

def test_pause_screen_resume_returns_to_playing() -> None:
    screen = PauseScreen(menu=Menu(options=["Resume", "Main Menu"]))

    result = screen.handle_event(key_event(pygame.K_RETURN))

    assert result == GameState.PLAYING


def test_pause_screen_escape_resumes_playing() -> None:
    screen = PauseScreen(menu=Menu(options=["Resume", "Main Menu"]))

    result = screen.handle_event(key_event(pygame.K_ESCAPE))

    assert result == GameState.PLAYING


def test_pause_screen_main_menu_option() -> None:
    screen = PauseScreen(menu=Menu(options=["Resume", "Main Menu"]))
    screen.handle_event(key_event(pygame.K_DOWN))

    result = screen.handle_event(key_event(pygame.K_RETURN))

    assert result == GameState.MENU


# --- InstructionsScreen --------------------------------------------------------

def test_instructions_screen_escape_returns_to_menu() -> None:
    screen = InstructionsScreen()

    result = screen.handle_event(key_event(pygame.K_ESCAPE))

    assert result == GameState.MENU


def test_instructions_screen_enter_returns_to_menu() -> None:
    screen = InstructionsScreen()

    result = screen.handle_event(key_event(pygame.K_RETURN))

    assert result == GameState.MENU


# --- GameOverScreen name entry + navigation ----------------------------------

def test_game_over_screen_starts_in_name_entry_mode() -> None:
    screen = GameOverScreen(menu=Menu(options=["Retry", "Main Menu"]))

    assert screen.entering_name is True
    assert screen.name == ""


def test_game_over_screen_typing_builds_name() -> None:
    screen = GameOverScreen(menu=Menu(options=["Retry", "Main Menu"]))

    type_text(screen, "OMAR")

    assert screen.name == "OMAR"


def test_game_over_screen_backspace_removes_last_character() -> None:
    screen = GameOverScreen(menu=Menu(options=["Retry", "Main Menu"]))
    type_text(screen, "AB")

    screen.handle_event(key_event(pygame.K_BACKSPACE))

    assert screen.name == "A"


def test_game_over_screen_menu_navigation_disabled_while_entering_name() -> None:
    screen = GameOverScreen(menu=Menu(options=["Retry", "Main Menu"]))

    screen.handle_event(key_event(pygame.K_DOWN))

    assert screen.menu.selected_index == 0


def test_game_over_screen_confirm_keeps_name_and_reveals_menu() -> None:
    screen = GameOverScreen(menu=Menu(options=["Retry", "Main Menu"]))
    type_text(screen, "AL")

    screen.handle_event(key_event(pygame.K_RETURN))

    assert screen.entering_name is False
    assert screen.name == "AL"


def test_game_over_screen_cancel_clears_name_and_reveals_menu() -> None:
    screen = GameOverScreen(menu=Menu(options=["Retry", "Main Menu"]))
    type_text(screen, "ZZ")

    screen.handle_event(key_event(pygame.K_ESCAPE))

    assert screen.entering_name is False
    assert screen.name == ""


def test_game_over_screen_enter_on_empty_name_keeps_name_entry() -> None:
    screen = GameOverScreen(menu=Menu(options=["Retry", "Main Menu"]))

    screen.handle_event(key_event(pygame.K_RETURN))

    assert screen.entering_name is True
    assert screen.name == ""


def test_game_over_screen_menu_works_after_confirming_name() -> None:
    screen = GameOverScreen(menu=Menu(options=["Retry", "Main Menu"]))
    type_text(screen, "AL")
    screen.handle_event(key_event(pygame.K_RETURN))

    result = screen.handle_event(key_event(pygame.K_RETURN))

    assert result == GameState.PLAYING


def test_game_over_screen_reset_restarts_name_entry() -> None:
    screen = GameOverScreen(menu=Menu(options=["Retry", "Main Menu"]))
    type_text(screen, "AL")
    screen.handle_event(key_event(pygame.K_RETURN))

    screen.reset()

    assert screen.entering_name is True
    assert screen.name == ""


# --- VictoryScreen (mirrors GameOverScreen) ----------------------------------

def test_victory_screen_name_entry_and_navigation() -> None:
    screen = VictoryScreen(menu=Menu(options=["Retry", "Main Menu"]))

    assert screen.entering_name is True

    type_text(screen, "WIN")
    screen.handle_event(key_event(pygame.K_RETURN))
    assert screen.entering_name is False
    assert screen.name == "WIN"

    result = screen.handle_event(key_event(pygame.K_RETURN))
    assert result == GameState.PLAYING


def test_victory_screen_cancel_clears_name() -> None:
    screen = VictoryScreen(menu=Menu(options=["Retry", "Main Menu"]))
    type_text(screen, "X")

    screen.handle_event(key_event(pygame.K_ESCAPE))

    assert screen.name == ""
    assert screen.entering_name is False
