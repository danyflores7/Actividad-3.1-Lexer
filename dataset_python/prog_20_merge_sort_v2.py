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
