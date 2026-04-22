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
