# Simple calculator
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def calculator(num1, operator, num2):
    if operator == "+":
        return add(num1, num2)
    elif operator == "-":
        return subtract(num1, num2)
    elif operator == "*":
        return multiply(num1, num2)
    elif operator == "/":
        return divide(num1, num2)
    else:
        raise ValueError(f"Unknown operator: {operator}")

def main():
    operations = [(10, "+", 5), (10, "-", 3), (4, "*", 7), (20, "/", 4)]
    for a, op, b in operations:
        result = calculator(a, op, b)
        print(f"{a} {op} {b} = {result}")

if __name__ == "__main__":
    main()
