"""
Simple Ludo game implemented in Python.

This script implements a simplified, text‑based version of the classic
board game Ludo. It supports two to four players, each controlling one
token.  The objective is to move your token around the board and back
home.  You must roll a 6 to bring your token out of the yard, and you
must roll exact numbers to land exactly on the finishing square.

Rules implemented
=================

* Each player has a single token.  At the start of the game all
  tokens are in the yard.  A token in the yard is denoted by a step
  value of ``-1``.
* To move a token out of the yard onto the board, the player must
  roll a 6.  When a 6 is rolled and the token is in the yard the
  token moves to the player's starting square (step 0).  Rolling a
  6 grants the player an extra roll.  If the token is in the yard and
  the player does not roll a 6, the token remains in the yard and
  their turn ends.
* Once on the board, the token moves forward by the value of the die
  roll.  If the move would overshoot the finishing square, the token
  does not move.  You still get an extra roll when you roll a 6 even
  if the move overshoots.
* If your token lands on a square occupied by an opponent's token,
  that opponent's token is captured and sent back to the yard (step
  set to ``-1``).  Capturing an opponent does not grant an extra
  roll.
* A token that completes one full lap around the board (reaching
  ``step == board_length``) has finished.  The first player whose
  token finishes wins the game.

This implementation does **not** include the coloured home columns
found in the physical game; instead a single lap around the board is
treated as completion.  Safe squares and multiple tokens per player
are not implemented to keep the logic simple and easy to follow.

Usage
=====

Run the script directly using Python 3::

    python ludo.py

The game will prompt you for the number of players (2–4) and the
players' names.  It will then walk you through the turns, printing
the state of the board after each move.  Dice rolls are generated
using Python's :mod:`random` module.

Author: Ludo Game Developer
"""

import random
from typing import List, Tuple


class Player:
    """Represents a player in the Ludo game."""

    def __init__(self, name: str, start_index: int, board_length: int) -> None:
        self.name = name
        self.start_index = start_index
        self.board_length = board_length
        # step = -1 means the token is in the yard
        # step >= 0 means the token is on the board
        # step == board_length means the token has completed a full lap
        self.step: int = -1

    @property
    def is_finished(self) -> bool:
        """Return True if the player's token has completed a lap."""
        return self.step == self.board_length

    @property
    def on_board(self) -> bool:
        """Return True if the token is on the board (not in yard or finished)."""
        return 0 <= self.step < self.board_length

    def absolute_position(self) -> int:
        """
        Calculate the token's absolute position on the board.

        When the token is on the board, its absolute position is the
        player's start index plus the current step, modulo the length of the
        circular track.

        Returns ``-1`` if the token is in the yard or finished (for
        clarity when printing state).
        """
        if self.step < 0 or self.is_finished:
            return -1
        return (self.start_index + self.step) % self.board_length

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"Player(name={self.name!r}, step={self.step}, abs_pos={self.absolute_position()})"


class LudoGame:
    """
    A simplified Ludo game engine supporting 2–4 players.

    Each player controls one token.  Tokens start in the yard and must roll a
    6 to enter the board.  Players take turns rolling a six‑sided die and
    moving their token accordingly.  Landing on an opponent sends that
    opponent back to the yard.  The first player to complete a lap wins.
    """

    def __init__(self, players: List[Player], board_length: int = 52) -> None:
        self.players = players
        self.board_length = board_length
        self.current_index = 0
        # History of turns for debugging or future enhancements
        self.turn_history: List[Tuple[str, int]] = []

    def roll_die(self) -> int:
        """Roll a six‑sided die and return the value (1–6)."""
        return random.randint(1, 6)

    def play_turn(self, player: Player) -> bool:
        """
        Handle a single player's turn.

        Returns True if the player gets another turn (i.e., rolled a 6),
        otherwise False.
        """
        if player.is_finished:
            return False

        roll = self.roll_die()
        print(f"\n{player.name}'s turn. You rolled a {roll}.")
        self.turn_history.append((player.name, roll))

        # If the token is in the yard
        if player.step < 0:
            if roll == 6:
                player.step = 0  # move token onto the board
                print(f"{player.name} rolled a 6 and moved out of the yard!")
            else:
                print(f"{player.name}'s token is still in the yard. You need a 6 to move out.")
                return False
        else:
            proposed_step = player.step + roll
            if proposed_step > self.board_length:
                # Overshoot: cannot move
                print(f"{player.name} cannot move because you'd overshoot the finish.")
            elif proposed_step == self.board_length:
                # Finish the lap
                player.step = self.board_length
                print(f"{player.name} has completed a full lap and wins the game! Congratulations!")
                return False
            else:
                # Move token forward
                player.step = proposed_step
                print(f"{player.name} moves to step {player.step} (absolute position {player.absolute_position()}).")
                # Check for captures
                for other in self.players:
                    if other is player or not other.on_board:
                        continue
                    if other.absolute_position() == player.absolute_position():
                        other.step = -1
                        print(f"{player.name} captured {other.name}'s token! {other.name}'s token is sent back to the yard.")
                        break

        # Return True for extra turn when rolling a 6 and not finishing
        return roll == 6

    def print_board(self) -> None:
        """Print a simple representation of the board showing each token's position."""
        positions = ['.' for _ in range(self.board_length)]
        for p in self.players:
            abs_pos = p.absolute_position()
            if abs_pos >= 0:
                # Represent each player by the first letter of their name
                positions[abs_pos] = p.name[0].upper()
        track = ''.join(positions)
        print(f"Board: {track}")
        for p in self.players:
            status = "finished" if p.is_finished else ("in yard" if p.step < 0 else f"step {p.step}, abs {p.absolute_position()}")
            print(f"  {p.name}: {status}")

    def play(self) -> None:
        """Run the game loop until someone wins."""
        while True:
            player = self.players[self.current_index]
            extra_turn = self.play_turn(player)
            self.print_board()
            # Check if someone has finished
            if player.is_finished:
                break
            # Advance to next player unless the current player rolled a 6
            if not extra_turn:
                self.current_index = (self.current_index + 1) % len(self.players)


def setup_game() -> LudoGame:
    """
    Gather user input to configure the Ludo game.

    Prompts the user for the number of players (2–4) and their names.  Each
    player is assigned a different starting index on the board.  Returns
    a configured :class:`LudoGame` instance.
    """
    while True:
        try:
            num_players = int(input("Enter number of players (2–4): "))
            if 2 <= num_players <= 4:
                break
            print("Please enter a number between 2 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number between 2 and 4.")

    names = []
    for i in range(num_players):
        while True:
            name = input(f"Enter name for player {i + 1}: ").strip()
            if name:
                names.append(name)
                break
            print("Name cannot be empty. Please enter a valid name.")

    # Starting positions are evenly spaced around the board
    board_length = 52
    start_positions = [0, 13, 26, 39]
    players = [Player(name, start_positions[i], board_length) for i, name in enumerate(names)]
    return LudoGame(players, board_length)


def main() -> None:
    """Main entry point for running the Ludo game."""
    print("Welcome to the simplified Ludo game!")
    game = setup_game()
    game.play()


if __name__ == "__main__":
    main()