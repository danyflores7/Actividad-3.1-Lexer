# Stack data structure
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

def main():
    stack = Stack()
    for val in [1, 2, 3, 4, 5]:
        stack.push(val)
    print("Size:", stack.size())
    print("Top:", stack.peek())
    while not stack.is_empty():
        print("Popped:", stack.pop())

if __name__ == "__main__":
    main()
