"""
Full Ludo game implementation in Python (text‑based).

This module implements a more complete version of the Ludo board game
where each player has four tokens.  Players must race all four of
their tokens around the board and into their home column.  The first
player to move all four tokens to the finish wins.

The game logic is simplified but captures many of the core rules of
Ludo:

* 2–4 players, each with four tokens of one colour.
* Tokens start in the yard (off the board) and must roll a 6 to
  enter the board.
* Tokens move along a track of 52 squares before entering a home
  column of 6 squares unique to each player.
* Players must roll exactly the right number to land on the final
  square of the home column.
* Landing on an opponent’s token on the main track sends that token
  back to the yard, provided the destination square is not a safe
  square and the square is not occupied by two or more tokens.
* Safe squares (star squares) allow multiple tokens of any colour to
  occupy the square without capturing.
* Players cannot land on a square occupied by one of their own tokens
  on the main track (no stacking on the main track).  Stacking in
  home columns is allowed.
* Rolling a 6 or capturing an opponent grants an extra turn.

This implementation is text‑based.  It prints the state of the board
after each move and prompts the user to choose which token to move
when multiple moves are possible.

The primary goal of this code is to provide a clear and well
documented example of the game logic rather than a graphical user
interface.  Feel free to extend it with a GUI or additional features.
"""

import random
from typing import List, Optional, Tuple


class Token:
    """Represents a single Ludo token (coin)."""

    def __init__(self) -> None:
        # Step encoding:
        #  -1: token is in the yard (not yet on board)
        #   0–51: token is on the main board track
        #  52–57: token is in the player's home column (52 is the first home square)
        #  57: token has reached the finish (home)
        self.step: int = -1

    @property
    def in_yard(self) -> bool:
        return self.step < 0

    @property
    def in_home(self) -> bool:
        return self.step >= 52

    @property
    def is_finished(self) -> bool:
        return self.step == 57

    def absolute_position(self, start_index: int, board_length: int) -> Optional[int]:
        """
        Return the absolute board position (0–51) when the token is on the main
        track.  Returns None when the token is in the yard or in the home
        column.
        """
        if self.step < 0 or self.step >= 52:
            return None
        return (start_index + self.step) % board_length

    def __repr__(self) -> str:  # pragma: no cover
        return f"Token(step={self.step})"


class Player:
    """Represents a player in the full Ludo game."""

    def __init__(self, name: str, colour: str, start_index: int, home_entry: int, board_length: int, home_length: int = 6) -> None:
        self.name = name
        self.colour = colour
        self.start_index = start_index
        self.home_entry = home_entry  # index on main track just before entering home
        self.board_length = board_length
        self.home_length = home_length
        self.tokens: List[Token] = [Token() for _ in range(4)]

    @property
    def all_finished(self) -> bool:
        """Return True if all tokens have reached the finish."""
        return all(tok.is_finished for tok in self.tokens)

    def active_tokens(self) -> List[int]:
        """Return indices of tokens that are not finished (i.e. still in play or in yard)."""
        return [i for i, t in enumerate(self.tokens) if not t.is_finished]

    def __repr__(self) -> str:  # pragma: no cover
        return f"Player(name={self.name!r}, tokens={self.tokens})"


class LudoGameFull:
    """
    Manage a game of Ludo with 2–4 players and four tokens per player.

    This class encapsulates the game loop, turn handling, move validation,
    capturing, and victory conditions.
    """

    def __init__(self, players: List[Player], board_length: int = 52, home_length: int = 6) -> None:
        self.players = players
        self.board_length = board_length
        self.home_length = home_length
        self.current_player_index = 0
        # Safe squares are typically the coloured star squares.  We include the
        # starting squares for each player and the squares 8 positions ahead.
        start_positions = [p.start_index for p in players]
        second_safe = [(pos + 8) % board_length for pos in start_positions]
        self.safe_positions = set(start_positions + second_safe)

    def roll_die(self) -> int:
        return random.randint(1, 6)

    def get_board_occupants(self) -> dict:
        """
        Build a mapping from absolute board position (0–51) to a list of (player_index, token_index).
        Tokens in the yard or in home columns are excluded.
        """
        occupants: dict = {}
        for p_index, player in enumerate(self.players):
            for t_index, tok in enumerate(player.tokens):
                abs_pos = tok.absolute_position(player.start_index, self.board_length)
                if abs_pos is not None:
                    occupants.setdefault(abs_pos, []).append((p_index, t_index))
        return occupants

    def get_valid_tokens_for_roll(self, player_index: int, roll: int) -> List[int]:
        """
        Determine which tokens belonging to a player can be moved given the dice roll.

        Returns a list of token indices that represent valid moves.  If the list
        is empty, the player cannot move any token for this roll.
        """
        player = self.players[player_index]
        occupants = self.get_board_occupants()
        valid_tokens: List[int] = []
        for idx, tok in enumerate(player.tokens):
            if tok.is_finished:
                continue  # token already finished
            # Determine the proposed step if this token is moved
            if tok.in_yard:
                if roll != 6:
                    continue  # cannot move out of yard without a 6
                dest_step = 0
                dest_abs = player.start_index
                # Check if destination is blocked by player's own token on board
                blocked = False
                for other_idx, other_tok in enumerate(player.tokens):
                    if other_idx == idx or other_tok.in_yard or other_tok.in_home:
                        continue
                    if other_tok.absolute_position(player.start_index, self.board_length) == dest_abs:
                        blocked = True
                        break
                if blocked:
                    continue
                valid_tokens.append(idx)
            else:
                dest_step = tok.step + roll
                # Overshoot beyond final home square
                if dest_step > 51 + self.home_length:  # >57
                    continue
                # Moving within main track
                if dest_step < 52:
                    dest_abs = (player.start_index + dest_step) % self.board_length
                    # Check if dest square is safe
                    if dest_abs in self.safe_positions:
                        # Safe: allow stacking of tokens regardless of colour
                        # Always valid (no capturing in safe squares)
                        valid_tokens.append(idx)
                        continue
                    # Count occupants at dest
                    occ = occupants.get(dest_abs, [])
                    # Blocked if any of your own tokens already occupy dest
                    blocked_by_self = any(p_idx == player_index for p_idx, _ in occ)
                    if blocked_by_self:
                        continue
                    # Blocked if dest has more than one opponent token
                    # or dest has two tokens of any colour (stack) on main track
                    if len(occ) > 1:
                        continue
                    # Otherwise dest is valid (capture if exactly one opponent token)
                    valid_tokens.append(idx)
                else:
                    # dest_step in home column (52–57)
                    # Need to check if dest_step exactly equals 57 when finishing; overshoot already filtered
                    # Check if destination in home column is already occupied by another token of this player
                    # For simplicity, allow stacking in home column
                    valid_tokens.append(idx)
        return valid_tokens

    def move_token(self, player_index: int, token_index: int, roll: int) -> bool:
        """
        Move the specified token for the given player by the number rolled.

        Returns True if the player gets another turn (i.e. rolled a 6 or captured an opponent).
        """
        player = self.players[player_index]
        token = player.tokens[token_index]
        occupants = self.get_board_occupants()
        extra_turn = False
        capture_occurred = False

        if token.in_yard:
            # Move out of yard to start square
            token.step = 0
            print(f"{player.name} moves a token out of the yard to the start square.")
            extra_turn = True  # Rolling a 6 when in yard grants another turn
        else:
            dest_step = token.step + roll
            if dest_step < 52:
                dest_abs = (player.start_index + dest_step) % self.board_length
                # Check safe square
                if dest_abs in self.safe_positions:
                    # No capturing in safe squares
                    token.step = dest_step
                    print(f"{player.name}'s token moves to safe square {dest_abs} (step {dest_step}).")
                else:
                    occ = occupants.get(dest_abs, [])
                    # If one opponent token is present, capture
                    if occ and len(occ) == 1 and occ[0][0] != player_index:
                        opp_player_idx, opp_token_idx = occ[0]
                        opp_player = self.players[opp_player_idx]
                        opp_token = opp_player.tokens[opp_token_idx]
                        opp_token.step = -1
                        capture_occurred = True
                        print(f"{player.name} captures {opp_player.name}'s token at square {dest_abs}!")
                    # Move token to dest
                    token.step = dest_step
                    print(f"{player.name}'s token moves to square {dest_abs} (step {dest_step}).")
            else:
                # Move within home column (dest_step 52–57)
                token.step = dest_step
                if dest_step == 57:
                    print(f"{player.name}'s token has reached the finish!")
                else:
                    print(f"{player.name}'s token moves to home square {dest_step - 52} (step {dest_step}).")
        # Determine extra turn: rolling 6 or capturing
        if roll == 6 or capture_occurred:
            extra_turn = True
        return extra_turn

    def print_board(self) -> None:
        """
        Print a simple representation of the current state of the board.

        The board is represented as a list of 52 squares.  Each square
        displays which tokens occupy it.  Home columns and yard tokens
        are displayed separately for each player.
        """
        occupants = self.get_board_occupants()
        # Represent main track
        track_repr = []
        for pos in range(self.board_length):
            occ = occupants.get(pos, [])
            if not occ:
                track_repr.append(".")
            else:
                # Represent each occupant by the first letter of its player's colour
                # If multiple tokens, represent by number of tokens
                if len(occ) == 1:
                    p_idx, _ = occ[0]
                    track_repr.append(self.players[p_idx].colour[0].upper())
                else:
                    track_repr.append(str(len(occ)))
        print("Main track (0–51):")
        # print in segments of 13 for readability
        for i in range(0, self.board_length, 13):
            print(' '.join(track_repr[i:i+13]))
        # Represent each player's tokens
        for p in self.players:
            print(f"{p.name} ({p.colour}):")
            for idx, tok in enumerate(p.tokens):
                if tok.in_yard:
                    status = "yard"
                elif tok.is_finished:
                    status = "finished"
                elif tok.in_home:
                    status = f"home {tok.step - 52}"
                else:
                    abs_pos = tok.absolute_position(p.start_index, self.board_length)
                    status = f"track pos {abs_pos} (step {tok.step})"
                print(f"  Token {idx + 1}: {status}")

    def play(self) -> None:
        """
        Run the game loop until a player wins.
        """
        while True:
            player = self.players[self.current_player_index]
            print(f"\n{player.name}'s turn ({player.colour}).")
            extra_turn = False
            roll = self.roll_die()
            print(f"You rolled a {roll}.")
            valid_tokens = self.get_valid_tokens_for_roll(self.current_player_index, roll)
            if not valid_tokens:
                print("No valid moves available for this roll.")
                # Check extra turn on 6 even if no move
                if roll == 6:
                    print("You rolled a 6 but cannot move. You get another roll anyway.")
                    extra_turn = True
                else:
                    extra_turn = False
            else:
                # Ask player to choose token if multiple valid
                if len(valid_tokens) == 1:
                    chosen_idx = valid_tokens[0]
                    print(f"Moving token {chosen_idx + 1} automatically.")
                else:
                    print("Tokens that can move:")
                    for idx in valid_tokens:
                        tok = player.tokens[idx]
                        if tok.in_yard:
                            desc = "yard"
                        elif tok.in_home:
                            desc = f"home {tok.step - 52}"
                        else:
                            abs_pos = tok.absolute_position(player.start_index, self.board_length)
                            desc = f"track pos {abs_pos} (step {tok.step})"
                        print(f"  {idx + 1}: {desc}")
                    while True:
                        try:
                            choice = int(input(f"Select the token to move (1–{len(player.tokens)}): ")) - 1
                            if choice in valid_tokens:
                                chosen_idx = choice
                                break
                            else:
                                print("Invalid selection. Choose one of the movable tokens.")
                        except ValueError:
                            print("Invalid input. Please enter a number.")
                # Move the chosen token
                extra_turn = self.move_token(self.current_player_index, chosen_idx, roll)
            # Print board after move
            self.print_board()
            # Check if current player has won
            if player.all_finished:
                print(f"\n{player.name} has moved all tokens home and wins the game! Congratulations!")
                break
            # Decide if we move to next player
            if not extra_turn:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)


def setup_full_game() -> LudoGameFull:
    """
    Interactive setup for a full Ludo game with 2–4 players.
    Prompts for names and assigns colours in order: red, green, yellow, blue.
    """
    colours = ["red", "green", "yellow", "blue"]
    start_positions = [0, 13, 26, 39]
    # Home entry is the square just before a player's start index (moving backwards)
    # It is used in more advanced versions of Ludo where tokens must enter the home column
    # from that square.  We compute it for completeness.
    board_length = 52
    home_entries = [ (start - 1) % board_length for start in start_positions ]
    while True:
        try:
            num = int(input("Enter number of players (2–4): "))
            if 2 <= num <= 4:
                break
            print("Please enter a number between 2 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    players: List[Player] = []
    for i in range(num):
        while True:
            name = input(f"Enter name for player {i + 1} ({colours[i]}): ").strip()
            if name:
                break
            print("Name cannot be empty.")
        players.append(Player(name, colours[i], start_positions[i], home_entries[i], board_length))
    return LudoGameFull(players, board_length)


def main() -> None:
    print("Welcome to Full Ludo Game!")
    game = setup_full_game()
    game.play()


if __name__ == "__main__":
    main()