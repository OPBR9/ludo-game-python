# Ludo Game Project

This repository contains two Python implementations of the classic
board game **Ludo**:

* **`ludo.py`** – a simplified game in which each player controls a
  single token.  The goal is to move your token around the board
  once and back to your starting square.  Landing on an opponent
  captures their token, and rolling a 6 grants an extra turn.
* **`ludo_full.py`** – a more complete game that follows the
  traditional Ludo rules: each player has four tokens, there are
  safe squares, a full lap around the board is followed by a
  colour‑coded home column, and the first player to bring all four
  tokens home wins.  Capturing an opponent or rolling a 6 grants
  another turn.

## Features (simplified version)

* 2–4 human players.
* Each player controls one token.
* Roll a 6 to move out of the yard.
* Landing on an opponent captures their token and sends it back to the
  yard.
* Rolling a 6 grants an extra turn.
* The first player to complete one lap around the board wins.

> **Note:** The simplified version does not include home columns or
> safe squares, nor does it support multiple tokens per player.
> See `ludo_full.py` for a more complete implementation.

## Requirements

* Python 3.7 or later.
* No external dependencies are required—only the Python standard
  library.

## Running the game

Clone this repository or download the `ludo_game` directory, then run
one of the following commands in your terminal:

**Simplified version**

```bash
python ludo.py
```

**Full version**

```bash
python ludo_full.py
```

Both scripts will prompt you for the number of players (between 2
and 4) and their names.  Players take turns rolling a die, and the
game prints the state of the board after each move.  In the full
version you may be asked which token to move when multiple moves are
possible.

## Contributing

Feel free to fork this repository and submit pull requests if you
would like to improve the game, fix bugs, or add new features such as
GUI support, multiple tokens per player, AI opponents, or home
columns.  Contributions are welcome!

## License

This project is licensed under the MIT License.  See the
[`LICENSE`](LICENSE) file for details.