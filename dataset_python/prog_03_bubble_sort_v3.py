# Bubble sort with swap count
def bubble_sort(numbers):
    size = len(numbers)
    swaps = 0
    for pass_num in range(size):
        for idx in range(0, size - pass_num - 1):
            if numbers[idx] > numbers[idx + 1]:
                numbers[idx], numbers[idx + 1] = numbers[idx + 1], numbers[idx]
                swaps += 1
    return numbers, swaps

def run():
    values = [64, 34, 25, 12, 22, 11, 90]
    print("Before:", values)
    sorted_values, total_swaps = bubble_sort(values)
    print("After:", sorted_values)
    print("Swaps:", total_swaps)

if __name__ == "__main__":
    run()
