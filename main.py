#Python Tutorial: Calculator with Advanced Mapping Logic
#This tutorial will guide you through building a simple calculator in Python, 
#but with a twist: we'll use a more advanced mapping logic to make our code cleaner and more extensible.

import math
import datetime

#===============================================
#Step 1: Define the Architecture
#Instead of a long list of if/else statements, we will use a Dictionary Mapping strategy. 
#This is a common pattern in system design to make code more extensible.

#Component   |   Responsibility
#Logic Layer    |   Pure functions that perform math.
#Operation Map  |   A dictionary linking symbols (like +) to functions.
#Input Handler  |   Validates that user input is actually a number.
#Main Loop      |   Keeps the program running until the user quits.
#===============================================

#===============================================
#Step 2: Create the Math Logic
#We'll start by defining our core operations.
#Note the safety check in the division function.
#===============================================

def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b

#===============================================
#Complex Math (The math Module)
#===============================================
def power(a, b):
    return math.pow(a, b)

def square_root(a, _): # We use '_' because our logic expects two numbers, but sqrt only needs one
    if a < 0:
        raise ValueError("Cannot take square root of a negative number!")
    return math.sqrt(a)

#add a "Clear Memory" command so you can reset the last_result to zero without restarting
def clear_memory(a=None, b=None):
    """Resets the calculator state to zero."""
    print("Memory Cleared!")
    return 0

#===============================================
#Step 4: The Advanced Map Logic This is where the "Advanced" part comes in.
#By mapping strings to functions, you can add new features (like square roots or exponents) later just by adding one line to this dictionary.
#===============================================

operations = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide,
    "pow": power,
    "sqrt": square_root,
    "c": clear_memory  # <--- New command added here
}

#===============================================
#Implementing the Infinite Loop
#===============================================

def calculator():
    while True:
        print("\n--- Advanced Calculator ---")
        # 1. Get User Input
        operation = input("Enter operation (+, -, *, /) or 'q' to quit: ").lower()

        # 2. Exit Strategy
        if operation == 'q':
            print("Shutting down. Goodbye!")
            break

        if operation not in ['+', '-', '*', '/']:
            print("Invalid operation. Please try again.")
            continue

        # 3. Get Numbers using our validator
        num1 = get_number("Enter first number: ")
        num2 = get_number("Enter second number: ")

        # 4. Perform Calculation
        try:
            if operation == '+':
                print(f"Result: {add(num1, num2)}")
            elif operation == '-':
                print(f"Result: {subtract(num1, num2)}")
            # ... and so on
        except Exception as e:
            print(f"An error occurred: {e}")

#The "History" Logger

def log_calculation(num1, op, num2, result):
    """Logs the calculation with a timestamp to a text file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {num1} {op} {num2} = {result}\n"
    
    with open("calculator_history.txt", "a") as file:
        file.write(log_entry)

# --- LOGIC LAYER ---
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b): return a / b if b != 0 else "Error: Div by 0"
def power(a, b): return math.pow(a, b)
def square_root(a, b=None): return math.sqrt(a) if a >= 0 else "Error: Neg sqrt"
def clear_memory(a=None, b=None): return 0

# --- DATA LAYER ---
operations = {
    "+": add, "-": subtract, "*": multiply, "/": divide,
    "pow": power, "sqrt": square_root, "c": clear_memory
}

#===============================================
#Adding the Memory Feature
#===============================================
# Initialize memory at the very top of your script
last_result = 0

def get_number(prompt):
    global last_result # Tells Python we want to use the variable outside this function
    while True:
        user_input = input(prompt).lower().strip()
        
        if user_input == 'ans':
            print(f" (Using last result: {last_result})")
            return last_result

        try:
            return float(user_input)
        except ValueError:
            print("Invalid input! Enter a number or 'ans'.")

#The "Help" Command
def display_help():
    print("\n--- Available Commands ---")
    print("+    : Addition")
    print("-    : Subtraction")
    print("* : Multiplication")
    print("/    : Division")
    print("pow  : Power (Num1 to the power of Num2)")
    print("sqrt : Square Root of Num1")
    print("c    : Clear Memory")
    print("h    : View Session History (from file)")
    print("help : Show this menu")
    print("q    : Quit")

#===============================================
#Step 5: Putting it all Together
#Now we'll create the main loop that ties everything together.
#===============================================

def main():
    global last_result
    print("Commands: +, -, *, /, pow, sqrt | 'c' to Clear | 'q' to Quit")
    
    while True:
        op = input("\nOperation: ").lower().strip()
        
        if op == 'q': break
        
        if op == 'c':
            last_result = clear_memory()
            continue

        if op not in operations:
            print("Invalid command.")
            continue

        num1 = get_number("Num 1: ")
        # Only ask for second number if it's not a square root
        num2 = get_number("Num 2: ") if op != 'sqrt' else 0

        last_result = operations[op](num1, num2)
        print(f"Result: {last_result}")


if __name__ == "__main__":
    main()