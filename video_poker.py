import tkinter as tk
import random

PALOS = ["♠", "♥", "♦", "♣"]      #son los 4 palos de la baraja. Es un dato fijo.

# Fisher-Yates: recorre la lista de atrás hacia adelante e intercambia
# cada carta con otra al azar de las que todavía no se han fijado.     
def barajar(lista):                  
    for i in range(len(lista) - 1, 0, -1):               
        j = random.randint(0, i)                  
        lista[i], lista[j] = lista[j], lista[i]              


class Carta:
    def __init__(self, palo, valor):        #crea la carta. Lo hace con el palo y el valor que le pasemos.
        self.palo = palo                    #lo vamos a ocupar para saber el palo de la carta. Lo hacemos con self.palo para que sea un atributo de la clase. 
        self.valor = valor

    def texto(self):                        #Transforma el valor de la carta en un texto. Si es 11, 12, 13 o 14, lo transforma en J, Q, K o A. Si no, lo transforma en el número que le corresponde.
        if self.valor == 11:
            return "J"
        elif self.valor == 12:
            return "Q"
        elif self.valor == 13:
            return "K"
        elif self.valor == 14:
            return "A"
        else:
            return str(self.valor)

    def __str__(self):                       #Devuelve una representación en cadena de la carta. por ejemplo, si la carta es un 10 de corazones, devuelve "10♥". Si es un As de tréboles, devuelve "A♣".
        return f"{self.texto()}{self.palo}"

class Mazo:                                  #crea un mazo de cartas. Lo hace con una lista de cartas, que se llena con todas las combinaciones posibles de palos y valores.
    def __init__(self):
        self.cartas = []                       #empieza con una lista vacía de cartas.
        for palo in PALOS:                      # por cada palo en la lista de palos, crea una carta con ese palo y un valor del 2 al 14 (inclusive).
            for valor in range(2, 15):          #en cada iteración, crea una carta con el palo y el valor correspondiente, y la agrega a la lista de cartas del mazo.
                self.cartas.append(Carta(palo, valor)) # en la lista de cartas del mazo, agrega la carta creada.
        barajar(self.cartas)                       #después de crear todas las cartas, baraja el mazo usando la función barajar() que definimos antes.
    def sacar(self):                            #saca una carta del mazo. Lo hace con el método pop() de la lista de cartas, que elimina y devuelve el último elemento de la lista.
        return self.cartas.pop()                


#Evaluar la mano de poker. Devuelve un diccionario con el conteo de cada valor en la mano.
def contar_valores(mano):
    conteo = {}
    for carta in mano:
        conteo[carta.valor] = conteo.get(carta.valor, 0) + 1
    return conteo

#detectar color. Devuelve True si todas las cartas tienen el mismo palo, False en caso contrario.
def es_color(mano):
    primer_palo = mano[0].palo
    for carta in mano:
        if carta.palo != primer_palo:
            return False
    return True


def es_escalera(mano):
    valores = []
    for carta in mano:
        valores.append(carta.valor)

    unicos = sorted(set(valores))
    if len(unicos) == 5 and unicos[-1] - unicos[0] == 4:
        return True
    if unicos == [2, 3, 4, 5, 14]:  # Caso especial: A-2-3-4-5
        return True
    return False


def evaluar_mano(mano):
    conteo = contar_valores(mano)
    valores = list(conteo.values())
    es_color_mano = es_color(mano)
    es_escalera_mano = es_escalera(mano)

    if es_color_mano and es_escalera_mano and min(conteo) == 10:
        return "Escalera real"
    elif es_color_mano and es_escalera_mano:
        return "Escalera de color"
    elif 4 in valores:
        return "Poker"
    elif 3 in valores and 2 in valores:
        return "Full"
    elif es_color_mano:
        return "Color"
    elif es_escalera_mano:
        return "Escalera"
    elif 3 in valores:
        return "Trio"
    elif valores.count(2) == 2:
        return "Doble pareja"
    for valor, veces in conteo.items():
        if veces == 2 and valor >= 11:
            return "Pareja"
    return "None"
# el for con .items() itera sobre los pares clave-valor del diccionario conteo, donde valor es la clave (el valor de la carta) y veces es el valor (el número de veces que aparece esa carta en la mano). Si encuentra una carta que aparece exactamente 2 veces y su valor es mayor o igual a 11 (J, Q, K o A), devuelve "Pareja". Si no se cumple ninguna de las condiciones anteriores, devuelve "None".
#return solo llega a la linea sin ninguna condicion anterior devolvio algo
#la cadena puede terminar antes de llegar a la linea final, si alguna condicion se cumple y devuelve algo. Si ninguna condicion se cumple, llega a la linea final y devuelve "None".


class VideoPoker(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        titulo = tk.Label(self, text="Video Poker", font=("Arial", 24, "bold"))
        titulo.pack(pady=10)

        self.lbl_cartas = tk.Label(self, text="", font=("Arial", 28))
        self.lbl_cartas.pack(pady=10)

        self.lbl_resultado = tk.Label(self, text="Presiona 'Repartir' para jugar", font=("Arial", 16))
        self.lbl_resultado.pack(pady=5)

        boton = tk.Button(self, text="Repartir", font=("Arial", 14), command=self.repartir)
        boton.pack(pady=10)

    def repartir(self):
        mazo = Mazo()
        mano = []
        for _ in range(5):
            mano.append(mazo.sacar())
        self.lbl_cartas.config(text=" ".join(str(carta) for carta in mano))
        resultado = evaluar_mano(mano)
        if resultado == "None":
            self.lbl_resultado.config(text="Sin premio")
        else:
            self.lbl_resultado.config(text=resultado)

if __name__ == "__main__":
    ventana = tk.Tk()
    ventana.title("Video Poker")
    VideoPoker(ventana).pack(padx=20, pady=20)
    ventana.mainloop()


