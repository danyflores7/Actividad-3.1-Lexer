"""
Generador de dataset: 20 programas Python con alta similitud.
Crea variantes de algoritmos clásicos con pequeñas modificaciones
(renombrado de variables, cambios de literales, reordenamiento).
Ejecutar: python generar_dataset.py
"""
import os
from pathlib import Path

PROGRAMS = {

"prog_01_bubble_sort.py": '''\
# Bubble Sort implementation
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def main():
    data = [64, 34, 25, 12, 22, 11, 90]
    print("Original:", data)
    sorted_data = bubble_sort(data)
    print("Sorted:", sorted_data)

if __name__ == "__main__":
    main()
''',

"prog_02_bubble_sort_v2.py": '''\
# Ordenamiento de burbuja
def ordenamiento_burbuja(lista):
    n = len(lista)
    for i in range(n):
        for j in range(0, n - i - 1):
            if lista[j] > lista[j + 1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
    return lista

def ejecutar():
    numeros = [64, 34, 25, 12, 22, 11, 90]
    print("Sin ordenar:", numeros)
    resultado = ordenamiento_burbuja(numeros)
    print("Ordenado:", resultado)

if __name__ == "__main__":
    ejecutar()
''',

"prog_03_bubble_sort_v3.py": '''\
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
''',

"prog_04_fibonacci.py": '''\
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
''',

"prog_05_fibonacci_v2.py": '''\
# Secuencia de Fibonacci
def calcular_fibonacci(cantidad):
    serie = []
    primero, segundo = 0, 1
    for _ in range(cantidad):
        serie.append(primero)
        primero, segundo = segundo, primero + segundo
    return serie

def mostrar_fibonacci(limite):
    numeros = calcular_fibonacci(limite)
    for i, valor in enumerate(numeros):
        print(f"F({i}) = {valor}")

if __name__ == "__main__":
    mostrar_fibonacci(15)
''',

"prog_06_fibonacci_v3.py": '''\
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
''',

"prog_07_binary_search.py": '''\
# Binary search algorithm
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def main():
    data = [2, 3, 4, 10, 40, 50, 60, 70]
    target = 10
    result = binary_search(data, target)
    if result != -1:
        print(f"Element {target} found at index {result}")
    else:
        print(f"Element {target} not found")

if __name__ == "__main__":
    main()
''',

"prog_08_binary_search_v2.py": '''\
# Búsqueda binaria
def busqueda_binaria(lista, objetivo):
    izquierda, derecha = 0, len(lista) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        if lista[medio] == objetivo:
            return medio
        elif lista[medio] < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return -1

def ejecutar():
    datos = [2, 3, 4, 10, 40, 50, 60, 70]
    buscado = 10
    indice = busqueda_binaria(datos, buscado)
    if indice != -1:
        print(f"Elemento {buscado} encontrado en índice {indice}")
    else:
        print(f"Elemento {buscado} no encontrado")

if __name__ == "__main__":
    ejecutar()
''',

"prog_09_stack.py": '''\
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
''',

"prog_10_stack_v2.py": '''\
# Pila (estructura de datos)
class Pila:
    def __init__(self):
        self.elementos = []

    def apilar(self, elemento):
        self.elementos.append(elemento)

    def desapilar(self):
        if not self.esta_vacia():
            return self.elementos.pop()
        return None

    def tope(self):
        if not self.esta_vacia():
            return self.elementos[-1]
        return None

    def esta_vacia(self):
        return len(self.elementos) == 0

    def tamano(self):
        return len(self.elementos)

def ejecutar():
    pila = Pila()
    for val in [1, 2, 3, 4, 5]:
        pila.apilar(val)
    print("Tamaño:", pila.tamano())
    print("Tope:", pila.tope())
    while not pila.esta_vacia():
        print("Desapilado:", pila.desapilar())

if __name__ == "__main__":
    ejecutar()
''',

"prog_11_linked_list.py": '''\
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
''',

"prog_12_linked_list_v2.py": '''\
# Lista enlazada simple
class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.siguiente = None

class ListaEnlazada:
    def __init__(self):
        self.cabeza = None

    def agregar(self, valor):
        nuevo_nodo = Nodo(valor)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
            return
        actual = self.cabeza
        while actual.siguiente:
            actual = actual.siguiente
        actual.siguiente = nuevo_nodo

    def mostrar(self):
        elementos = []
        actual = self.cabeza
        while actual:
            elementos.append(str(actual.valor))
            actual = actual.siguiente
        print(" -> ".join(elementos))

    def longitud(self):
        contador = 0
        actual = self.cabeza
        while actual:
            contador += 1
            actual = actual.siguiente
        return contador

def ejecutar():
    lista = ListaEnlazada()
    for val in [10, 20, 30, 40, 50]:
        lista.agregar(val)
    lista.mostrar()
    print("Longitud:", lista.longitud())

if __name__ == "__main__":
    ejecutar()
''',

"prog_13_calculator.py": '''\
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
''',

"prog_14_calculator_v2.py": '''\
# Calculadora básica
def sumar(a, b):
    return a + b

def restar(a, b):
    return a - b

def multiplicar(a, b):
    return a * b

def dividir(a, b):
    if b == 0:
        raise ValueError("No se puede dividir entre cero")
    return a / b

def calculadora(num1, operador, num2):
    if operador == "+":
        return sumar(num1, num2)
    elif operador == "-":
        return restar(num1, num2)
    elif operador == "*":
        return multiplicar(num1, num2)
    elif operador == "/":
        return dividir(num1, num2)
    else:
        raise ValueError(f"Operador desconocido: {operador}")

def principal():
    operaciones = [(10, "+", 5), (10, "-", 3), (4, "*", 7), (20, "/", 4)]
    for a, op, b in operaciones:
        resultado = calculadora(a, op, b)
        print(f"{a} {op} {b} = {resultado}")

if __name__ == "__main__":
    principal()
''',

"prog_15_matrix_multiply.py": '''\
# Matrix multiplication
def matrix_multiply(A, B):
    rows_A = len(A)
    cols_A = len(A[0])
    cols_B = len(B[0])
    result = [[0] * cols_B for _ in range(rows_A)]
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                result[i][j] += A[i][k] * B[k][j]
    return result

def print_matrix(matrix):
    for row in matrix:
        print(" ".join(map(str, row)))

def main():
    A = [[1, 2, 3], [4, 5, 6]]
    B = [[7, 8], [9, 10], [11, 12]]
    C = matrix_multiply(A, B)
    print("Result:")
    print_matrix(C)

if __name__ == "__main__":
    main()
''',

"prog_16_matrix_multiply_v2.py": '''\
# Multiplicación de matrices
def multiplicar_matrices(A, B):
    filas_A = len(A)
    cols_A = len(A[0])
    cols_B = len(B[0])
    resultado = [[0] * cols_B for _ in range(filas_A)]
    for i in range(filas_A):
        for j in range(cols_B):
            for k in range(cols_A):
                resultado[i][j] += A[i][k] * B[k][j]
    return resultado

def imprimir_matriz(matriz):
    for fila in matriz:
        print(" ".join(map(str, fila)))

def principal():
    A = [[1, 2, 3], [4, 5, 6]]
    B = [[7, 8], [9, 10], [11, 12]]
    C = multiplicar_matrices(A, B)
    print("Resultado:")
    imprimir_matriz(C)

if __name__ == "__main__":
    principal()
''',

"prog_17_prime_sieve.py": '''\
# Sieve of Eratosthenes
def sieve_of_eratosthenes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [num for num, prime in enumerate(is_prime) if prime]

def main():
    limit = 100
    primes = sieve_of_eratosthenes(limit)
    print(f"Primes up to {limit}: {primes}")
    print(f"Count: {len(primes)}")

if __name__ == "__main__":
    main()
''',

"prog_18_prime_sieve_v2.py": '''\
# Criba de Eratóstenes
def criba_eratostenes(limite):
    es_primo = [True] * (limite + 1)
    es_primo[0] = es_primo[1] = False
    for i in range(2, int(limite ** 0.5) + 1):
        if es_primo[i]:
            for j in range(i * i, limite + 1, i):
                es_primo[j] = False
    return [num for num, primo in enumerate(es_primo) if primo]

def principal():
    limite = 100
    primos = criba_eratostenes(limite)
    print(f"Primos hasta {limite}: {primos}")
    print(f"Cantidad: {len(primos)}")

if __name__ == "__main__":
    principal()
''',

"prog_19_merge_sort.py": '''\
# Merge sort implementation
def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def main():
    data = [38, 27, 43, 3, 9, 82, 10]
    print("Original:", data)
    sorted_data = merge_sort(data)
    print("Sorted:", sorted_data)

if __name__ == "__main__":
    main()
''',

"prog_20_merge_sort_v2.py": '''\
# Ordenamiento por mezcla
def combinar(izquierda, derecha):
    resultado = []
    i = j = 0
    while i < len(izquierda) and j < len(derecha):
        if izquierda[i] <= derecha[j]:
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1
    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])
    return resultado

def ordenamiento_mezcla(arr):
    if len(arr) <= 1:
        return arr
    medio = len(arr) // 2
    izquierda = ordenamiento_mezcla(arr[:medio])
    derecha = ordenamiento_mezcla(arr[medio:])
    return combinar(izquierda, derecha)

def principal():
    datos = [38, 27, 43, 3, 9, 82, 10]
    print("Original:", datos)
    ordenados = ordenamiento_mezcla(datos)
    print("Ordenado:", ordenados)

if __name__ == "__main__":
    principal()
''',
}

def main():
    out_dir = Path("dataset_python")
    out_dir.mkdir(exist_ok=True)
    for filename, code in PROGRAMS.items():
        path = out_dir / filename
        path.write_text(code, encoding='utf-8')
        print(f"  Creado: {path}")
    print(f"\n✓ Dataset generado en '{out_dir}/' ({len(PROGRAMS)} archivos)")

if __name__ == "__main__":
    main()
