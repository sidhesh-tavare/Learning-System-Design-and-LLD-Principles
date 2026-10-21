"""Tic-Tac-Toe: reference solution for LLD mock #1.

Who owns what:
    Mark / Player   -> plain data
    Board           -> cells only; refuses any move that breaks board rules
    WinningStrategy -> "did this move win?" (swappable rule)
    Game            -> turns, game rules, result
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto


class Mark(Enum):
    X = "X"
    O = "O"


class GameState(Enum):
    IN_PROGRESS = auto()
    WON = auto()
    DRAW = auto()


class InvalidMoveError(Exception):
    """Raised for any rejected move. The caller can't silently ignore it, unlike a printed message."""


# Same behaviour, different data -> one class, many objects (no Player1/Player2 subclasses).
@dataclass(frozen=True)
class Player:
    name: str
    mark: Mark


class Board:
    def __init__(self, size: int = 3) -> None:
        if size < 3:
            raise ValueError("Board size must be at least 3")
        self.size = size
        # None = empty cell. One sentinel, used everywhere.
        self._grid: list[list[Mark | None]] = [[None] * size for _ in range(size)]
        self._filled = 0

    def place(self, row: int, col: int, mark: Mark) -> None:
        # Board guards its own data, so no caller can ever corrupt it.
        # Explicit bounds check: grid[-1] is valid Python and would hit the wrong cell.
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise InvalidMoveError(f"({row}, {col}) is off the board")
        if self._grid[row][col] is not None:
            raise InvalidMoveError(f"({row}, {col}) is already taken")
        self._grid[row][col] = mark
        self._filled += 1

    def get(self, row: int, col: int) -> Mark | None:
        return self._grid[row][col]

    def is_full(self) -> bool:
        return self._filled == self.size * self.size

    def __str__(self) -> str:
        return "\n".join(
            " | ".join(cell.value if cell else "." for cell in row) for row in self._grid
        )


class WinningStrategy(ABC):
    """Strategy seam: the answer to "what if the win rule changes?" (e.g. 4-in-a-row on 10x10)."""

    @abstractmethod
    def is_winner(self, board: Board, row: int, col: int, mark: Mark) -> bool: ...


class FullLineWinStrategy(WinningStrategy):
    """Win = a full row, column or diagonal. Only the lines through the LAST move are checked: O(n), not O(n^2)."""

    def is_winner(self, board: Board, row: int, col: int, mark: Mark) -> bool:
        n = board.size
        lines = [
            [(row, c) for c in range(n)],
            [(r, col) for r in range(n)],
        ]
        if row == col:
            lines.append([(i, i) for i in range(n)])
        if row + col == n - 1:
            lines.append([(i, n - 1 - i) for i in range(n)])
        return any(all(board.get(r, c) is mark for r, c in line) for line in lines)


class Game:
    def __init__(self, players: list[Player], board: Board, win_rule: WinningStrategy) -> None:
        if len(players) < 2:
            raise ValueError("Need at least 2 players")
        if len({p.mark for p in players}) != len(players):
            raise ValueError("Each player needs a unique mark")
        # Dependencies are injected (DIP), so tests can pass a 4x4 board or a different rule.
        self._board = board
        self._win_rule = win_rule
        self._turns: deque[Player] = deque(players)
        self.state = GameState.IN_PROGRESS
        self.winner: Player | None = None

    @property
    def current_player(self) -> Player:
        return self._turns[0]

    def play(self, row: int, col: int) -> GameState:
        # Game guards game rules; Board guards board rules.
        if self.state is not GameState.IN_PROGRESS:
            raise InvalidMoveError("Game is already over")

        player = self.current_player
        self._board.place(row, col, player.mark)  # raises -> we never reach rotate()

        if self._win_rule.is_winner(self._board, row, col, player.mark):
            self.state = GameState.WON
            self.winner = player
        elif self._board.is_full():
            self.state = GameState.DRAW
        else:
            self._turns.rotate(-1)  # turn passes ONLY after a valid, non-final move
        return self.state

    def __str__(self) -> str:
        return str(self._board)


def run_scripted(title: str, game: Game, moves: list[tuple[int, int]]) -> None:
    print(f"\n=== {title} ===")
    for row, col in moves:
        player = game.current_player
        try:
            game.play(row, col)
            print(f"{player.name} ({player.mark.value}) -> ({row}, {col})")
        except InvalidMoveError as err:
            print(f"{player.name} ({player.mark.value}) -> ({row}, {col}) REJECTED: {err}")
    print(game)
    if game.state is GameState.WON:
        print(f"Result: {game.winner.name} wins")
    elif game.state is GameState.DRAW:
        print("Result: draw")
    else:
        print("Result: still in progress")


def main() -> None:
    sid, ava = Player("Sid", Mark.X), Player("Ava", Mark.O)
    rule = FullLineWinStrategy()

    # Win, with invalid moves mixed in: taken cell, off-board, and a move after the game ends.
    run_scripted(
        "3x3 win + invalid moves",
        Game([sid, ava], Board(3), rule),
        [(0, 0), (1, 1), (0, 0), (5, 5), (0, 1), (2, 2), (0, 2), (2, 0)],
    )

    run_scripted(
        "3x3 draw",
        Game([sid, ava], Board(3), rule),
        [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (1, 2), (2, 1), (2, 0), (2, 2)],
    )

    # N x N follow-up: zero code changes, just a different Board.
    run_scripted(
        "4x4 column win",
        Game([sid, ava], Board(4), rule),
        [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0)],
    )


if __name__ == "__main__":
    main()
