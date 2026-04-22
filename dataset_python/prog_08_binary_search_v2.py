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
