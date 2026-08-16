# Open Questions

## Graphics library
- Use pygame as the graphical library.
- Keep pygame usage limited to functions with MLX-equivalent capabilities.
- Document the pygame functions we rely on during implementation.

## Maze generator integration
- Confirm the exact public API we will use from mazegenerator 2.1.0.
- Confirm coordinate conventions used by the package versus our `(x, y)` convention.
- Decide how to choose reachable spawn cells near the center and corners when the literal cells are blocked.
- Decide whether LevelData should preserve raw wall masks permanently or whether Grid should normalize them further.

## Gameplay decisions
- Decide what happens when the level timer reaches zero.
- Decide the frightened-mode duration.
- Decide the eaten-ghost respawn delay.
- Decide exact cheat keys and which cheats we will implement.

## Packaging
- Decide the packaging tool and target platform for the unlisted/private build.