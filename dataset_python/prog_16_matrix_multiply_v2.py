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
