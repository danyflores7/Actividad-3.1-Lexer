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
