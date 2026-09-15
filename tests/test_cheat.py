import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.cheat import CheatController  # noqa: E402

pygame.init()


def key_event(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def press_sequence(controller: CheatController, keys: list[int]) -> None:
    for key in keys:
        controller.handle_event(key_event(key))


ARROW_SEQUENCE = [
    pygame.K_UP, pygame.K_UP,
    pygame.K_DOWN, pygame.K_DOWN,
    pygame.K_LEFT, pygame.K_RIGHT,
    pygame.K_LEFT, pygame.K_RIGHT,
]

WASD_SEQUENCE = [
    pygame.K_w, pygame.K_w,
    pygame.K_s, pygame.K_s,
    pygame.K_a, pygame.K_d,
    pygame.K_a, pygame.K_d,
]


def test_cheat_controller_starts_disabled() -> None:
    controller = CheatController()

    assert controller.enabled is False
    assert controller.invincible is False
    assert controller.ghosts_frozen is False
    assert controller.speed_boosted is False


def test_non_keydown_events_are_ignored() -> None:
    controller = CheatController()

    controller.handle_event(pygame.event.Event(pygame.MOUSEMOTION))

    assert controller.enabled is False


def test_secret_sequence_via_arrows_enables_cheats() -> None:
    controller = CheatController()

    press_sequence(controller, ARROW_SEQUENCE)

    assert controller.enabled is True


def test_secret_sequence_via_wasd_enables_cheats() -> None:
    controller = CheatController()

    press_sequence(controller, WASD_SEQUENCE)

    assert controller.enabled is True


def test_wrong_sequence_does_not_enable_cheats() -> None:
    controller = CheatController()

    press_sequence(controller, ARROW_SEQUENCE[:-1])

    assert controller.enabled is False


def test_shuffled_sequence_does_not_enable_cheats() -> None:
    controller = CheatController()

    press_sequence(
        controller,
        [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT] * 2,
    )

    assert controller.enabled is False


def test_f_keys_do_nothing_while_disabled() -> None:
    controller = CheatController()

    controller.handle_event(key_event(pygame.K_F1))
    controller.handle_event(key_event(pygame.K_F2))
    controller.handle_event(key_event(pygame.K_F3))
    controller.handle_event(key_event(pygame.K_F4))
    controller.handle_event(key_event(pygame.K_F5))

    assert controller.invincible is False
    assert controller.ghosts_frozen is False
    assert controller.speed_boosted is False
    assert controller.consume_extra_life_request() is False
    assert controller.consume_level_skip_request() is False


def test_f1_toggles_invincible_when_enabled() -> None:
    controller = CheatController()
    press_sequence(controller, ARROW_SEQUENCE)

    controller.handle_event(key_event(pygame.K_F1))
    assert controller.invincible is True

    controller.handle_event(key_event(pygame.K_F1))
    assert controller.invincible is False


def test_f2_toggles_ghosts_frozen_when_enabled() -> None:
    controller = CheatController()
    press_sequence(controller, ARROW_SEQUENCE)

    controller.handle_event(key_event(pygame.K_F2))
    assert controller.ghosts_frozen is True

    controller.handle_event(key_event(pygame.K_F2))
    assert controller.ghosts_frozen is False


def test_f4_toggles_speed_boosted_when_enabled() -> None:
    controller = CheatController()
    press_sequence(controller, ARROW_SEQUENCE)

    controller.handle_event(key_event(pygame.K_F4))
    assert controller.speed_boosted is True

    controller.handle_event(key_event(pygame.K_F4))
    assert controller.speed_boosted is False


def test_f3_extra_life_is_one_shot() -> None:
    controller = CheatController()
    press_sequence(controller, ARROW_SEQUENCE)

    controller.handle_event(key_event(pygame.K_F3))

    assert controller.consume_extra_life_request() is True
    assert controller.consume_extra_life_request() is False


def test_f5_level_skip_is_one_shot() -> None:
    controller = CheatController()
    press_sequence(controller, ARROW_SEQUENCE)

    controller.handle_event(key_event(pygame.K_F5))

    assert controller.consume_level_skip_request() is True
    assert controller.consume_level_skip_request() is False


def test_disabling_resets_all_sub_cheats() -> None:
    controller = CheatController()
    press_sequence(controller, ARROW_SEQUENCE)
    controller.handle_event(key_event(pygame.K_F1))
    controller.handle_event(key_event(pygame.K_F2))
    controller.handle_event(key_event(pygame.K_F4))
    assert controller.invincible is True
    assert controller.ghosts_frozen is True
    assert controller.speed_boosted is True

    press_sequence(controller, ARROW_SEQUENCE)

    assert controller.enabled is False
    assert controller.invincible is False
    assert controller.ghosts_frozen is False
    assert controller.speed_boosted is False
