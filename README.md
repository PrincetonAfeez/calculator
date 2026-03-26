# Advanced Python CLI Calculator

A modular, stateful command-line calculator with persistent history and memory support.

## Features

- Basic math: `+`, `-`, `*`, `/`
- Extended math: `//` (floor division), `%` (modulo), `pow`, `sqrt`, `abs`, `fact`
- Percentage helper: `pct` (`a pct b` means `a% of b`)
- Memory support: use `ans` in place of a number
- Persistent history in `history.txt`
- Built-in commands for viewing and clearing history

## Commands

Math commands:

- `+`, `-`, `*`, `/`, `//`, `%`, `pow`, `sqrt`, `abs`, `fact`, `pct`

System commands:

- `help` - Show command help
- `h` - Show history
- `hc` - Clear history file
- `c` - Clear memory (`ans = 0`)
- `q` - Quit

## Installation

```bash
git clone https://github.com/PrincetonAfeez/calculator.git
cd calculator
```

## Usage

```bash
python main.py
```

## Project Structure

- `main.py` - minimal entrypoint
- `app.py` - CLI loop, history handling, and migration
- `operations.py` - calculator math operations and validation
- `tests/` - pytest test suite

Example workflow:

1. Enter a command (for example: `+`)
2. Provide first number
3. Provide second number (for two-operand commands)
4. Read result and reuse it with `ans`

Example:

- `pow` with `2` and `8` -> `256`
- `sqrt` with `ans` -> `16`
- `20 pct 150` -> `30`

## Notes

- Division, floor division, and modulo by zero are handled gracefully.
- Factorial only accepts non-negative whole numbers.
- `history.txt` is runtime data and should not be versioned.
- On startup, the app auto-migrates old history entries to the current format.

## Testing

```bash
pytest -q
```