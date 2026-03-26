#!/usr/bin/env python3
"""
Snake, but tidy.

- Arrow keys to move.
- Press R to restart on the game-over screen, or ESC/Q to quit.
- Food never spawns inside the snake.
- No instant 180° turns (classic snake rules).
"""

import random
from dataclasses import dataclass
from typing import Deque, List, Tuple, Set
from collections import deque

import pygame

# ---------------------------- Config ---------------------------------

GRID = 20                   # size of one grid cell (px)
BOARD_W, BOARD_H = 600, 400 # window size (px); should be multiples of GRID
FPS = 12                    # snake speed (frames per second)

BG_COLOR   = (14, 14, 14)
SNAKE_HEAD = (60, 200, 120)
SNAKE_BODY = (40, 160, 100)
FOOD_COLOR = (220, 60, 60)
INK        = (235, 235, 235)
INK_DIM    = (160, 160, 160)

FONT_NAME = "comicsansms"   # pick your poison, pffft
FONT_SIZE = 24

# ---------------------------- Types ----------------------------------

Vec = Tuple[int, int]

# ---------------------------- Helpers --------------------------------

def grid_positions(width: int, height: int, cell: int) -> Tuple[int, int]:
    """Return number of columns, rows for a given grid."""
    return width // cell, height // cell


def clamp_to_grid(x: int, y: int) -> Vec:
    """Snap a pixel position to grid coordinates (cells, not pixels)."""
    return x // GRID, y // GRID


def to_pixels(cell_pos: Vec) -> Vec:
    """Convert grid coordinates back to pixels (top-left of cell)."""
    cx, cy = cell_pos
    return cx * GRID, cy * GRID


def random_empty_cell(cols: int, rows: int, blocked: Set[Vec]) -> Vec:
    """Pick a random cell not in 'blocked'. Falls back gracefully if needed."""
    free = [(x, y) for x in range(cols) for y in range(rows) if (x, y) not in blocked]
    return random.choice(free) if free else (0, 0)

# ---------------------------- Game -----------------------------------

@dataclass
class Snake:
    body: Deque[Vec]         # leftmost is head
    direction: Vec           # delta in grid units, e.g., (1, 0)
    pending: Deque[Vec]      # queued direction changes

    def head(self) -> Vec:
        return self.body[0]

    def move(self, grow: bool = False) -> None:
        hx, hy = self.head()
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.appendleft(new_head)
        if not grow:
            self.body.pop()

    def queue_turn(self, new_dir: Vec) -> None:
        """Queue a turn if it’s not a 180° into yourself and not duplicate."""
        if not self.pending or self.pending[-1] != new_dir:
            self.pending.append(new_dir)

    def apply_turn_if_valid(self) -> None:
        """Apply first queued turn that doesn’t reverse current direction."""
        if not self.pending:
            return
        nx, ny = self.pending[0]
        cx, cy = self.direction
        # prevent immediate 180° turn
        if (nx, ny) != (-cx, -cy):
            self.direction = (nx, ny)
            self.pending.popleft()

# ---------------------------- Main App --------------------------------

class SnakeGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Snake — cleaned up")
        self.screen = pygame.display.set_mode((BOARD_W, BOARD_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

        self.cols, self.rows = grid_positions(BOARD_W, BOARD_H, GRID)

        self.reset()

    def reset(self) -> None:
        start = (self.cols // 2, self.rows // 2)
        # Start heading right; snake length 1
        self.snake = Snake(body=deque([start]), direction=(1, 0), pending=deque())
        self.score = 0
        self.food = self._spawn_food()
        self.alive = True

    # ------------------------ Game Loop ------------------------------

    def run(self) -> None:
        while True:
            if self.alive:
                self._tick_play()
            else:
                if not self._tick_game_over():
                    break  # user quit from game-over screen
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

    # ------------------------ States --------------------------------

    def _tick_play(self) -> None:
        self._handle_play_events()

        self.snake.apply_turn_if_valid()
        next_head = self._next_head()

        # collisions: walls
        if not (0 <= next_head[0] < self.cols and 0 <= next_head[1] < self.rows):
            self.alive = False
            self._draw()  # draw final frame behind game-over overlay
            return

        # collisions: self
        if next_head in list(self.snake.body):
            self.alive = False
            self._draw()
            return

        # move & check food
        will_grow = next_head == self.food
        self.snake.move(grow=will_grow)

        if will_grow:
            self.score += 1
            self.food = self._spawn_food()

        self._draw()

    def _tick_game_over(self) -> bool:
        """Return False to quit, True to stay in loop."""
        self._draw()
        self._draw_game_over_overlay()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    self.reset()
        return True

    # ------------------------ Events --------------------------------

    def _handle_play_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    raise SystemExit
                # directions
                if event.key == pygame.K_LEFT:
                    self.snake.queue_turn((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.snake.queue_turn((1, 0))
                elif event.key == pygame.K_UP:
                    self.snake.queue_turn((0, -1))
                elif event.key == pygame.K_DOWN:
                    self.snake.queue_turn((0, 1))

    # ------------------------ Drawing -------------------------------

    def _draw(self) -> None:
        self.screen.fill(BG_COLOR)

        # food
        fx, fy = to_pixels(self.food)
        pygame.draw.rect(self.screen, FOOD_COLOR, (fx, fy, GRID, GRID))

        # snake
        for i, (sx, sy) in enumerate(self.snake.body):
            px, py = to_pixels((sx, sy))
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(self.screen, color, (px, py, GRID, GRID))

        # score
        self._blit_text(f"Score: {self.score}", (8, 6), INK)

    def _draw_game_over_overlay(self) -> None:
        # semi-transparent overlay
        overlay = pygame.Surface((BOARD_W, BOARD_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        big = pygame.font.SysFont(FONT_NAME, 36)
        title = big.render("Game Over", True, INK)
        prompt = self.font.render("R = restart   |   ESC/Q = quit", True, INK_DIM)
        score_txt = self.font.render(f"Final Score: {self.score}", True, INK)

        cx = BOARD_W // 2
        cy = BOARD_H // 2
        self.screen.blit(title, title.get_rect(center=(cx, cy - 30)))
        self.screen.blit(score_txt, score_txt.get_rect(center=(cx, cy + 5)))
        self.screen.blit(prompt, prompt.get_rect(center=(cx, cy + 40)))

    def _blit_text(self, text: str, pos: Vec, color: Tuple[int, int, int]) -> None:
        surf = self.font.render(text, True, color)
        self.screen.blit(surf, pos)

    # ------------------------ Mechanics -----------------------------

    def _next_head(self) -> Vec:
        hx, hy = self.snake.head()
        dx, dy = self.snake.direction
        return (hx + dx, hy + dy)

    def _spawn_food(self) -> Vec:
        occupied = set(self.snake.body)
        return random_empty_cell(self.cols, self.rows, occupied)

# ---------------------------- Entry ----------------------------------

if __name__ == "__main__":
    SnakeGame().run()
