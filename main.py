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