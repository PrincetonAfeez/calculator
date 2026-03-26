#Python Tutorial: Calculator with Advanced Mapping Logic
#This tutorial will guide you through building a simple calculator in Python, 
#but with a twist: we'll use a more advanced mapping logic to make our code cleaner and more extensible.

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

import math # Import the math module for advanced operations like power and sqrt
import datetime # Import datetime to add timestamps to our history logs

# --- LOGIC LAYER (The "Engine" of the calculator) ---

def add(a, b): 
    return a + b # Standard addition

def subtract(a, b): 
    return a - b # Standard subtraction

def multiply(a, b): 
    return a * b # Standard multiplication

def divide(a, b): 
    if b == 0: # Guard clause to prevent the program from crashing
        return "Error: Division by zero is not allowed"
    return a / b

def power(a, b): 
    return math.pow(a, b) # Raises number 'a' to the power of 'b'

def square_root(a, b=None): 
    if a < 0: # Guard clause because square roots of negative numbers are imaginary
        return "Error: Cannot calculate square root of a negative number"
    return math.sqrt(a) # 'b' is ignored here to keep function signatures consistent

# --- DATA & STATE LAYER (Managing memory and storage) ---

last_result = 0 # This global variable acts as the "Memory" (ans) of the calculator

# The Operations Map: This dictionary links text commands to our actual functions
operations = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide,
    "pow": power,
    "sqrt": square_root
}

def log_calculation(n1, op, n2, res):
    """Opens history.txt in 'append' mode to save the session data."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("history.txt", "a") as f: # 'a' ensures we add to the file, not overwrite it
        f.write(f"[{timestamp}] {n1} {op} {n2} = {res}\n")

# --- INTERFACE LAYER (Handling User Interaction) ---

def get_number(prompt):
    """Ensures the user enters a valid number or the 'ans' keyword."""
    global last_result
    while True:
        user_input = input(prompt).lower().strip()
        if user_input == 'ans': # Check if user wants to use the stored memory
            return last_result
        try:
            return float(user_input) # Convert string input to a decimal number
        except ValueError:
            print("Invalid input! Please enter a number or 'ans'.")

def display_help():
    """Prints a clean menu of all available system commands."""
    print("\n" + "="*30)
    print("  CALCULATOR SYSTEM HELP")
    print("="*30)
    print("Commands: +, -, *, /, pow, sqrt")
    print("c    : Clear Memory")
    print("h    : View History File")
    print("help : Show this menu")
    print("q    : Quit Program")
    print("="*30)

def main():
    global last_result # Access the global memory variable
    display_help() # Show the menu once at start
    
    while True: # The Main Loop (REPL: Read-Eval-Print Loop)
        choice = input("\nEnter Command: ").lower().strip()
        
        if choice == 'q': # Exit strategy
            print("System shutting down. Goodbye!")
            break
            
        if choice == 'help':
            display_help()
            continue # Restart the loop to ask for a new command
            
        if choice == 'c':
            last_result = 0
            print("Memory cleared to 0.")
            continue

        if choice == 'h':
            print("\n--- Session History ---")
            try:
                with open("history.txt", "r") as f: # Open file in 'read' mode
                    print(f.read())
            except FileNotFoundError: # Handle case where no history exists yet
                print("No history recorded yet.")
            continue

        if choice in operations:
            # Step 1: Get inputs
            num1 = get_number("First Number (or 'ans'): ")
            # Only ask for a second number if it's not a square root operation
            num2 = get_number("Second Number (or 'ans'): ") if choice != 'sqrt' else 0
            
            # Step 2: Perform the calculation using the dictionary map
            result = operations[choice](num1, num2)
            
            # Step 3: Output and Log the results
            print(f"RESULT: {result}")
            
            # Only save and log if the result was a successful number
            if isinstance(result, (int, float)):
                last_result = result
                log_calculation(num1, choice, num2, result)
        else:
            print(f"Error: '{choice}' is not a valid command. Type 'help'.")

# This boilerplate ensures the script only runs if executed directly
if __name__ == "__main__": 
    main()
