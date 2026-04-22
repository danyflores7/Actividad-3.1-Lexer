# Fibonacci with memoization
memo = {}

def fibonacci(n):
    if n in memo:
        return memo[n]
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    memo[n] = sequence
    return sequence

def display_fibonacci(count):
    result = fibonacci(count)
    for i, val in enumerate(result):
        print(f"F({i}) = {val}")

if __name__ == "__main__":
    display_fibonacci(15)
