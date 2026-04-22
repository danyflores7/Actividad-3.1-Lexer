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
