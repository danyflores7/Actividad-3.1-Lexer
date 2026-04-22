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
