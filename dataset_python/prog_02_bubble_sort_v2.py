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
