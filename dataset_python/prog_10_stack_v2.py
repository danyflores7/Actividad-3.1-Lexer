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
