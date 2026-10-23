import tkinter as tk
import random

PALOS = ["♠", "♥", "♦", "♣"]        #son los 4 palos de la baraja. Es un dato fijo.
TABLA_PAGOS = {                     #es un diccionario que contiene las combinaciones de poker y sus pagos. Es un dato fijo.
    "Escalera real": 250,           #escalera real es la mejor mano posible en el poker. Se compone de las cartas 10, J, Q, K y A del mismo palo.
    "Escalera de color": 50,        #escalera de color es una mano que consiste en cinco cartas consecutivas del mismo palo, pero no necesariamente del 10 al As.
    "Poker": 25,                    #poker es una mano que consiste en cuatro cartas del mismo valor y una carta de cualquier otro valor.
    "Full": 9,                      #full es una mano que consiste en tres cartas del mismo valor y dos cartas de otro valor.
    "Color": 6,                     #color es una mano que consiste en cinco cartas del mismo palo, pero no necesariamente consecutivas.
    "Escalera": 4,                  #escalera es una mano que consiste en cinco cartas consecutivas de cualquier palo.
    "Trio": 3,                      #trio es una mano que consiste en tres cartas del mismo valor y dos cartas de cualquier otro valor.
    "Doble pareja": 2,              #doble pareja es una mano que consiste en dos pares de cartas del mismo valor y una carta de cualquier otro valor.
    "Pareja":  1                    #pareja es una mano que consiste en dos cartas del mismo valor y tres cartas de cualquier otro valor.
}

CREDITOS_INICIALES = 30           #con cuántos créditos empieza el jugador. Se usa al iniciar y al reiniciar.


# Fisher-Yates: recorre la lista de atrás hacia adelante e intercambia
# cada carta con otra al azar de las que todavía no se han fijado.     
def barajar(lista):                  
    for i in range(len(lista) - 1, 0, -1):               
        j = random.randint(0, i)                  
        lista[i], lista[j] = lista[j], lista[i]              


class Carta:                                #esto sirve para crear una carta. La carta tiene un palo y un valor. El palo es uno de los 4 palos de la baraja y el valor es un número del 2 al 14 (inclusive). El 11 es J, el 12 es Q, el 13 es K y el 14 es A.
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
    
    def color(self):                       
        if self.palo in ["♥", "♦"]:
            return "red"
        else:
            return "black"

class Mazo:                                             #crea un mazo de cartas. Lo hace con una lista de cartas, que se llena con todas las combinaciones posibles de palos y valores.
    def __init__(self):
        self.cartas = []                                #empieza con una lista vacía de cartas.
        for palo in PALOS:                              # por cada palo en la lista de palos, crea una carta con ese palo y un valor del 2 al 14 (inclusive).
            for valor in range(2, 15):                  #en cada iteración, crea una carta con el palo y el valor correspondiente, y la agrega a la lista de cartas del mazo.
                self.cartas.append(Carta(palo, valor))  # en la lista de cartas del mazo, agrega la carta creada.
        barajar(self.cartas)                            #después de crear todas las cartas, baraja el mazo usando la función barajar() que definimos antes.
    def sacar(self):                                    #saca una carta del mazo. Lo hace con el método pop() de la lista de cartas, que elimina y devuelve el último elemento de la lista.
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

# Evaluar la mano de poker. Devuelve el nombre de la combinación ganadora o "None" si no hay combinación ganadora.
def evaluar_mano(mano):
    conteo = contar_valores(mano)
    valores = list(conteo.values())
    es_color_mano = es_color(mano)
    es_escalera_mano = es_escalera(mano)
# esto es un conjunto de condiciones que evalúan la mano de poker y devuelven el nombre de la combinación ganadora. Se evalúa primero si es una escalera real, luego una escalera de color, luego un poker, un full, un color, una escalera, un trío, una doble pareja y finalmente una pareja. Si ninguna de estas condiciones se cumple, devuelve "None".
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

# Calcula cuánto paga una mano según la apuesta. La Escalera real con apuesta máxima (5) tiene un bono especial de 4000.
def calcular_premio(resultado, apuesta):
    if resultado == "Escalera real" and apuesta == 5:
        return 4000
    return TABLA_PAGOS.get(resultado, 0) * apuesta

class VideoPoker(tk.Frame): #esto sirve para crear la interfaz gráfica del juego de video poker. Hereda de tk.Frame, que es un contenedor de widgets de Tkinter. Dentro de esta clase se definen los métodos para inicializar la interfaz, mostrar las cartas, manejar las apuestas y evaluar la mano del jugador.
    def __init__(self, master=None):
        
        super().__init__(master)
        self.mazo = None
        self.mano = []
        self.creditos = CREDITOS_INICIALES  #inicializa los créditos del jugador con la constante CREDITOS_INICIALES. Esto significa que el jugador empieza con 100 créditos.
        self.apuesta = 1    #fija la apuesta inicial en 1. Esto significa que el jugador apuesta 1 crédito por cada mano de poker que juegue.
        self.puede_cambiar = False
        self.conservadas = [False] * 5  # Lista para rastrear qué cartas se conservan
        self.mano = []  # Lista para almacenar la mano actual del jugador
        self.mano_ganadora = None  # Variable para almacenar la mano ganadora
        titulo = tk.Label(self, text="Video Poker", font=("Arial", 24, "bold"))
        titulo.pack(pady=10)

        self.fondo_normal = titulo.cget("bg")  # Guardar el color de fondo normal del título
        self.texto_normal = titulo.cget("fg")  # Guardar el color de texto normal del título

        marco_cartas = tk.Frame(self)  # contenerdor para las cartas. Se crea un marco (marco_cartas) que contendrá las cartas de la mano del jugador. Se utiliza un Frame de Tkinter para agrupar los elementos visuales relacionados con las cartas.
        marco_cartas.pack(pady=10)
        self.botones_cartas = []
        self.etiquetas_conservar = []
        for i in range(5):
            boton = tk.Button(marco_cartas, text="?", font=("Arial", 28), width=3,
                              command=lambda pos=i: self.toggle_conservar(pos))
            boton.grid(row=0, column=i, padx=5)
            self.botones_cartas.append(boton)

            etiqueta = tk.Label(marco_cartas, text="", font=("Arial", 12, "bold"), fg="green")
            etiqueta.grid(row=1, column=i)
            self.etiquetas_conservar.append(etiqueta)

        self.lbl_resultado = tk.Label(self, text="Presiona 'Repartir' para jugar", font=("Arial", 16))
        self.lbl_resultado.pack(pady=5)
        self.lbl_creditos = tk.Label(self, text="", font=("Arial", 14))
        self.lbl_creditos.pack()
       

        mostrar_tabla = tk.Frame(self)
        mostrar_tabla.pack(pady=10)

        self.columnas_tabla = [[]for _ in range(5)]  # Crear una lista de listas para almacenar las etiquetas de cada columna
        self.filas_tabla = {}
        fila = 0
        for nombre, pago in TABLA_PAGOS.items():
            etiqueta_nombre = tk.Label(mostrar_tabla, text=nombre, font=("Arial", 11),   # CAMBIÓ
                                       width=16, anchor="w")
            etiqueta_nombre.grid(row=fila, column=0)
            self.filas_tabla[nombre] = [etiqueta_nombre]   # NUEVO: la fila empieza con su nombre

            for apuesta in range(1, 6):
                celda = tk.Label(mostrar_tabla, text=str(calcular_premio(nombre, apuesta)),                                 font=("Arial", 11), width=5)
                celda.grid(row=fila, column=apuesta)
                self.columnas_tabla[apuesta - 1].append(celda)
                self.filas_tabla[nombre].append(celda)     # NUEVO: la celda también es de la fila

            fila += 1  

            
        
        self.boton_apuesta = tk.Button(self, text="Subir Apuesta", font=("Arial", 14), command=self.subir_apuesta)
        self.boton_apuesta.pack(pady=5)
        self.boton_repartir = tk.Button(self, text="Repartir", font=("Arial", 14), command=self.repartir)
        self.boton_repartir.pack(pady=10)
        self.mostrar_creditos()  # Mostrar créditos iniciales   
        self.boton_cambiar = tk.Button(self, text="Cambiar", font=("Arial", 14), command=self.cambiar)
        self.boton_cambiar.pack(pady=5)
        self.boton_reiniciar = tk.Button(self, text="Jugar de nuevo", font=("Arial", 14), command=self.reiniciar)
        # no le hacemos .pack() todavía: queda escondido hasta que se acaben los créditos
    def mostrar_creditos(self):
        self.lbl_creditos.config(text=f"Créditos: {self.creditos} | Apuesta: {self.apuesta}")
        for i in range(5):                          # columna de la apuesta actual en amarillo
            for celda in self.columnas_tabla[i]:
                if i == self.apuesta - 1:
                    celda.config(bg="gold", fg="black")
                else:
                    celda.config(bg=self.fondo_normal, fg=self.texto_normal)
        for nombre, etiquetas in self.filas_tabla.items():
            if nombre == self.mano_ganadora:
                for etiqueta in etiquetas:                 # toda la fila en verde
                    etiqueta.config(bg="green", fg="white")
            else:
                etiquetas[0].config(bg=self.fondo_normal, fg=self.texto_normal)
    def subir_apuesta(self):
        if self.puede_cambiar:
            return  # si ya hay una mano activa, no hace nada
        self.apuesta = self.apuesta % 5 + 1  # Apuesta cíclica entre 1 y 5
        self.mostrar_creditos()  # Actualizar la visualización de créditos después de cambiar la apuesta
   
   
    def repartir(self):
        if self.puede_cambiar:
            return  # si ya hay una mano activa, no hace nada
        self.mano_ganadora = None
        if self.creditos < self.apuesta:
            self.lbl_resultado.config(text="No tienes suficientes créditos para apostar.")
            return
        self.creditos -= self.apuesta
        self.mostrar_creditos()  # Actualizar la visualización de créditos después de la apuesta

        self.mazo = Mazo()
        self.mano = [self.mazo.sacar() for _ in range(5)]
        for i in range(5):
            self.mostrar_carta(i)

        self.conservadas = [False] * 5                # limpiar marcas de la mano anterior
        for etiqueta in self.etiquetas_conservar:
            etiqueta.config(text="")

        self.lbl_resultado.config(text="Elige qué cartas conservar y presiona 'Cambiar'")
        self.puede_cambiar = True                     # empieza la fase de elegir


    def toggle_conservar(self, pos):
        if not self.puede_cambiar:
            return
        self.conservadas[pos] = not self.conservadas[pos]
        if self.conservadas[pos]:
            self.etiquetas_conservar[pos].config(text="Conservar")
        else:
            self.etiquetas_conservar[pos].config(text="")

    def cambiar(self):
        if not self.puede_cambiar:                 # si no hay mano activa, no hace nada
            return
        for i in range(5):
            if not self.conservadas[i]:            # solo las cartas NO conservadas
                self.mano[i] = self.mazo.sacar()   # se reemplaza la carta en esa posición
                self.mostrar_carta(i)

        resultado = evaluar_mano(self.mano)
        premio = calcular_premio(resultado, self.apuesta)      
        self.mano_ganadora = resultado
        self.mostrar_creditos()

        if premio > 0:
            self.lbl_resultado.config(text=f"¡{resultado}! Ganaste {premio} créditos.")
        else:
            self.lbl_resultado.config(text="No hay combinación ganadora.")

        self.puede_cambiar = False                 # la mano terminó
        if self.creditos == 0:                     # ya no puede pagar ni la apuesta mínima
            self.lbl_resultado.config(text="¡Fin del juego! Te quedaste sin créditos.")
            self.boton_reiniciar.pack(pady=5)      # ahora sí se muestra el botón
    
    def mostrar_carta(self, i):              # muestra la carta i en su botón, con su color
        carta = self.mano[i]
        self.botones_cartas[i].config(text=str(carta), fg=carta.color())


    def reiniciar(self):
        self.creditos = CREDITOS_INICIALES
        self.apuesta = 1
        self.mano = []
        self.mano_ganadora = None
        self.puede_cambiar = False
        self.conservadas = [False] * 5

        for i in range(5):                         # las cartas vuelven a "?"
            self.botones_cartas[i].config(text="?", fg=self.texto_normal)
            self.etiquetas_conservar[i].config(text="")

        self.lbl_resultado.config(text="Presiona 'Repartir' para jugar")
        self.mostrar_creditos()                    # actualiza créditos y colores de la tabla
        self.boton_reiniciar.pack_forget()         # esconde el botón otra vez

if __name__ == "__main__":
    ventana = tk.Tk()
    ventana.title("Video Poker")
    VideoPoker(ventana).pack(padx=20, pady=20)



    ventana.mainloop()

