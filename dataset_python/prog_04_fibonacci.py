# Fibonacci sequence generator
def fibonacci(n):
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence

def print_fibonacci(limit):
    result = fibonacci(limit)
    for i, val in enumerate(result):
        print(f"F({i}) = {val}")

if __name__ == "__main__":
    print_fibonacci(15)
