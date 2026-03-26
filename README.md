# Advanced Python CLI Calculator

A modular, stateful Command Line Interface (CLI) calculator built as part of the #100DaysOfCode challenge. This project demonstrates core System Architecture principles, including Layered Design, Persistent State, and File I/O.

## 🚀 Features

- **Standard Operations:** Addition, Subtraction, Multiplication, and Division.
- **Advanced Math:** Power (exponentiation) and Square Root functions using Python's `math` module.
- **State Management (Memory):** Use the `ans` keyword to use the previous calculation's result in your next equation.
- **Persistent History:** Automatically logs every successful calculation to `history.txt` with a timestamp.
- **Interactive Help:** Built-in `help` command to guide users through available operations.
- **Input Validation:** Robust error handling for "Division by Zero" and non-numeric inputs.

## 🏗️ System Architecture

The project follows a **Layered Architecture** pattern to ensure the code is maintainable and scalable:

1.  **Logic Layer:** Pure mathematical functions.
2.  **Data/State Layer:** Manages global memory (`last_result`) and file persistence (`history.txt`).
3.  **Interface Layer:** Handles the REPL (Read-Eval-Print Loop), user input validation, and console output.

## 🛠️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/PrincetonAfeez/calculator.git](https://github.com/PrincetonAfeez/calculator.git)
   cd calculator