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
