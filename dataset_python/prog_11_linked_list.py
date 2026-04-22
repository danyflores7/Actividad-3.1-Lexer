# Singly linked list
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def display(self):
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        print(" -> ".join(elements))

    def length(self):
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count

def main():
    ll = LinkedList()
    for val in [10, 20, 30, 40, 50]:
        ll.append(val)
    ll.display()
    print("Length:", ll.length())

if __name__ == "__main__":
    main()
