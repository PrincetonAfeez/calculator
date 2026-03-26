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
#Step 3: Build a Robust Input Validator
#In professional software, you can't trust user input.
#We use a try-except block to prevent the program from crashing if someone types "abc" instead of a number.
#===============================================

def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input! Please enter a numeric value.")

            

#===============================================
#Step 4: The Advanced Map Logic This is where the "Advanced" part comes in.
#By mapping strings to functions, you can add new features (like square roots or exponents) later just by adding one line to this dictionary.
#===============================================

operations = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide
}

#===============================================
#Step 5: Putting it all Together
#Now we'll create the main loop that ties everything together.
#===============================================

def main():
    print("Advanced Calculator")
    print("Supported operations: +, -, *, /")
    print("Type 'quit' to exit.")

    while True:
        # Get the first number
        num1 = get_number("Enter the first number: ")

        # Get the operation
        op = input("Enter an operation (+, -, *, /): ")

        # Check if the user wants to quit
        if op == "quit":
            print("Goodbye!")
            break

        # Check if the operation is valid
        if op not in operations:
            print("Invalid operation! Please try again.")
            continue

        # Get the second number
        num2 = get_number("Enter the second number: ")

        # Perform the calculation
        try:
            result = operations[op](num1, num2)
            print(f"Result: {result}")
        except ValueError as e:
            print(f"Error: {e}")

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

#===============================================
#Adding "State" (Memory)
#===============================================
last_result = 0

def get_number(prompt):
    while True:
        user_input = input(prompt).lower()
        if user_input == 'ans':
            return last_result
        try:
            return float(user_input)
        except ValueError:
            print("Please enter a number or 'ans'.")
            
if __name__ == "__main__":
    main()