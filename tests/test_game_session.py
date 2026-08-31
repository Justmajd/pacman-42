import pytest

from src.config import GameConfig, LevelConfig
from src.contracts import GameState, WorldEvent
from src.game_session import GameSession


def make_config(
    lives: int = 3,
    level_max_time: int = 90,
    frightened_duration: float = 6.0,
    level_count: int = 10,
) -> GameConfig:
    return GameConfig(
        lives=lives,
        level_max_time=level_max_time,
        frightened_duration=frightened_duration,
        levels=tuple(LevelConfig() for _ in range(level_count)),
    )


def test_initial_state() -> None:
    config = make_config(
        lives=3,
        level_max_time=90,
        frightened_duration=6.0,
    )

    session = GameSession(config)

    assert session.score == 0
    assert session.lives == 3
    assert session.level == 1
    assert session.level_time_remaining == 90
    assert session.frightened_time_remaining == 0.0
    assert session.state == GameState.PLAYING


def test_update_decreases_level_timer() -> None:
    session = GameSession(make_config(level_max_time=90))

    session.update(1.5)

    assert session.level_time_remaining == pytest.approx(88.5)


def test_update_decreases_frightened_timer() -> None:
    session = GameSession(make_config(frightened_duration=6.0))
    session.handle_event(WorldEvent.SUPER_PACGUM_EATEN)

    session.update(1.5)

    assert session.frightened_time_remaining == pytest.approx(4.5)


def test_frightened_timer_does_not_go_below_zero() -> None:
    session = GameSession(make_config(frightened_duration=6.0))
    session.handle_event(WorldEvent.SUPER_PACGUM_EATEN)

    session.update(10.0)

    assert session.frightened_time_remaining == 0.0


def test_timeout_causes_game_over() -> None:
    session = GameSession(make_config(level_max_time=90))

    session.update(100.0)

    assert session.level_time_remaining == 0.0
    assert session.state == GameState.GAME_OVER


def test_pacgum_event_adds_score() -> None:
    config = make_config()
    session = GameSession(config)

    session.handle_event(WorldEvent.PACGUM_EATEN)

    assert session.score == config.points_per_pacgum


def test_super_pacgum_event_adds_score_and_starts_frightened_mode() -> None:
    config = make_config(frightened_duration=6.0)
    session = GameSession(config)

    session.handle_event(WorldEvent.SUPER_PACGUM_EATEN)

    assert session.score == config.points_per_super_pacgum
    assert session.frightened_time_remaining == 6.0


def test_super_pacgum_refreshes_frightened_timer() -> None:
    config = make_config(frightened_duration=6.0)
    session = GameSession(config)

    session.handle_event(WorldEvent.SUPER_PACGUM_EATEN)
    session.update(4.0)

    assert session.frightened_time_remaining == pytest.approx(2.0)

    session.handle_event(WorldEvent.SUPER_PACGUM_EATEN)

    assert session.frightened_time_remaining == 6.0


def test_ghost_eaten_adds_score() -> None:
    config = make_config()
    session = GameSession(config)

    session.handle_event(WorldEvent.GHOST_EATEN)

    assert session.score == config.points_per_ghost


def test_player_hit_loses_one_life() -> None:
    session = GameSession(make_config(lives=3))

    session.handle_event(WorldEvent.PLAYER_HIT)

    assert session.lives == 2
    assert session.state == GameState.PLAYING


def test_last_life_causes_game_over() -> None:
    session = GameSession(make_config(lives=1))

    session.handle_event(WorldEvent.PLAYER_HIT)

    assert session.lives == 0
    assert session.state == GameState.GAME_OVER


def test_lives_do_not_go_below_zero() -> None:
    session = GameSession(make_config(lives=1))

    session.handle_event(WorldEvent.PLAYER_HIT)
    session.handle_event(WorldEvent.PLAYER_HIT)

    assert session.lives == 0
    assert session.state == GameState.GAME_OVER


def test_level_clear_advances_level_and_resets_timers() -> None:
    config = make_config(
        level_max_time=90,
        frightened_duration=6.0,
        level_count=3,
    )
    session = GameSession(config)

    session.score = 500
    session.lives = 2
    session.handle_event(WorldEvent.SUPER_PACGUM_EATEN)
    session.update(2.0)

    session.handle_event(WorldEvent.LEVEL_CLEARED)

    assert session.level == 2
    assert session.score == 500 + config.points_per_super_pacgum
    assert session.lives == 2
    assert session.level_time_remaining == 90
    assert session.frightened_time_remaining == 0.0
    assert session.state == GameState.PLAYING


def test_score_and_lives_persist_across_levels() -> None:
    config = make_config(level_count=3)
    session = GameSession(config)

    session.score = 1234
    session.lives = 2

    session.handle_event(WorldEvent.LEVEL_CLEARED)

    assert session.level == 2
    assert session.score == 1234
    assert session.lives == 2


def test_final_level_clear_causes_victory() -> None:
    config = make_config(level_count=2)
    session = GameSession(config)

    session.level = 2

    session.handle_event(WorldEvent.LEVEL_CLEARED)

    assert session.level == 2
    assert session.state == GameState.VICTORY