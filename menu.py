
# MENÚ PRINCIPA una sola ventana desde donde se escoge cada juego.
# Para agregar un juego: importarlo y ponerlo en JUEGOS.
 
import tkinter as tk
from video_poker import VideoPoker   
from cara_o_cruz import CaraOCruz
from casino_adivina import casinoadivina
from ariana_game import arianagame

# NUEVO es cara o cruz de dennys
# from ruleta import Ruleta          # ejemplo para los demás juegos
import estilos                       # colores y fuentes
 
JUEGOS = [                           # (texto del botón, clase sin paréntesis)
    ("Video Poker", VideoPoker),
    ("Cara o Cruz", CaraOCruz), 
    ("casino adivina", casinoadivina),
    ("ariana game", arianagame),
 
 # esto se agrega en cada juego que se vaya agregando
    # ("Ruleta", Ruleta),
]
 
 
class Casino(tk.Tk):                          # la única ventana del proyecto
    def __init__(self):
        super().__init__()
        self.title("Casino")
        self.configure(bg=estilos.FONDO)
        self.minsize(500, 450)
        self.pantalla_actual = None           # esto eslo que se va a ver ahora (menú o juego)
        self.mostrar_menu()
 
    def cambiar_pantalla(self, nueva):        # borra la pantalla actual y pone la nueva
        if self.pantalla_actual is not None:
            self.pantalla_actual.destroy()
        self.pantalla_actual = nueva
        self.pantalla_actual.pack(padx=20, pady=20)
 
    def mostrar_menu(self):
        menu = tk.Frame(self, bg=estilos.FONDO)
 
        tk.Label(menu, text="♠  ♥  ♦  ♣", font=("Arial", 22),
                 bg=estilos.FONDO, fg=estilos.DORADO).pack(pady=(10, 0))
        tk.Label(menu, text="CASINO", font=estilos.FUENTE_TITULO,
                 bg=estilos.FONDO, fg=estilos.DORADO).pack()
        tk.Label(menu, text="Elige tu juego", font=estilos.FUENTE_SUBTITULO,
                 bg=estilos.FONDO, fg=estilos.TEXTO).pack(pady=(0, 25))
 
        for nombre, ClaseJuego in JUEGOS:    # un botón por juego
            # clase=ClaseJuego: cada botón guarda su propio juego
            tk.Button(menu, text=nombre, font=estilos.FUENTE_BOTON, width=20,
                      command=lambda clase=ClaseJuego: self.mostrar_juego(clase)).pack(pady=5)
 
        tk.Button(menu, text="Salir", font=("Arial", 14), width=10,
                  command=self.destroy).pack(pady=20)
        self.cambiar_pantalla(menu)
 
    def mostrar_juego(self, ClaseJuego):     # sirve para cualquier juego
        pantalla = tk.Frame(self, bg=estilos.FONDO)
        ClaseJuego(pantalla).pack()          # aquí se crea el juego
        tk.Button(pantalla, text="Volver al menú", font=("Arial", 12),
                  command=self.mostrar_menu).pack(pady=10)
        self.cambiar_pantalla(pantalla)
 
 
if __name__ == "__main__":                   # ejecutar este archivo para jugar
    app = Casino()
    app.mainloop()
    app = Casino()
    app.mainloop()
