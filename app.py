import datetime
import re

from operations import CalculatorError, OPERATIONS

HISTORY_FILE = "history.txt"
OLD_FORMAT_PATTERN = re.compile(
    r"^\[(?P<timestamp>[^\]]+)\]\s+"
    r"(?P<left>-?\d+(?:\.\d+)?)\s+"
    r"(?P<op>\S+)\s+"
    r"(?P<right>-?\d+(?:\.\d+)?)\s*=\s*"
    r"(?P<result>.+)$"
)


def _normalize_number_text(number_text):
    value = float(number_text)
    if value.is_integer():
        return f"{int(value)}.0"
    return str(value)


def migrate_history_line(line):
    stripped = line.strip()
    match = OLD_FORMAT_PATTERN.match(stripped)
    if not match:
        return stripped

    timestamp = match.group("timestamp")
    left = _normalize_number_text(match.group("left"))
    op = match.group("op")
    right = _normalize_number_text(match.group("right"))
    result = match.group("result").strip()

    if op == "sqrt":
        return f"[{timestamp}] sqrt {left} = {result}"
    return f"[{timestamp}] {op} {left} {right} = {result}"


def migrate_history_file(file_path=HISTORY_FILE):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            original_lines = file.readlines()
    except FileNotFoundError:
        return 0

    migrated_lines = [migrate_history_line(line) + "\n" for line in original_lines]
    changes = sum(
        1 for old, new in zip(original_lines, migrated_lines) if old != new
    )

    if changes:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(migrated_lines)
    return changes


def log_calculation(command, args, result):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    args_str = " ".join(str(arg) for arg in args)
    with open(HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {command} {args_str} = {result}\n")


def show_history():
    print("\n--- Session History ---")
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()
            print(content if content else "History file is empty.")
    except FileNotFoundError:
        print("No history recorded yet.")


def clear_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        file.write("")
    print("History file cleared.")


def get_number(prompt, last_result):
    while True:
        user_input = input(prompt).lower().strip()
        if user_input == "ans":
            return last_result
        try:
            return float(user_input)
        except ValueError:
            print("Invalid input! Please enter a number or 'ans'.")


def display_help():
    print("\n" + "=" * 42)
    print("            CALCULATOR HELP")
    print("=" * 42)
    print("Math Commands:")
    print("  +, -, *, /, //, %, pow, sqrt, abs, fact, pct")
    print("  pct usage example: 20 pct 150 = 30")
    print("\nSystem Commands:")
    print("  c     : Clear memory (ans = 0)")
    print("  h     : View history")
    print("  hc    : Clear history")
    print("  hm    : Migrate old history format")
    print("  help  : Show this menu")
    print("  q     : Quit")
    print("=" * 42)


def main():
    last_result = 0.0
    display_help()
    migrated = migrate_history_file()
    if migrated:
        print(f"Migrated {migrated} history entr{'y' if migrated == 1 else 'ies'}.")

    while True:
        command = input("\nEnter Command: ").lower().strip()

        if command == "q":
            print("System shutting down. Goodbye!")
            break

        if command == "help":
            display_help()
            continue

        if command == "c":
            last_result = 0.0
            print("Memory cleared to 0.")
            continue

        if command == "h":
            show_history()
            continue

        if command == "hc":
            clear_history()
            continue

        if command == "hm":
            changed = migrate_history_file()
            print(f"Migrated {changed} history entr{'y' if changed == 1 else 'ies'}.")
            continue

        if command not in OPERATIONS:
            print(f"Error: '{command}' is not a valid command. Type 'help'.")
            continue

        operation = OPERATIONS[command]
        args = [get_number("First Number (or 'ans'): ", last_result)]
        if operation["arity"] == 2:
            args.append(get_number("Second Number (or 'ans'): ", last_result))

        try:
            result = operation["fn"](*args)
            print(f"RESULT: {result}")
            last_result = float(result)
            log_calculation(command, args, result)
        except CalculatorError as error:
            print(f"Error: {error}")
