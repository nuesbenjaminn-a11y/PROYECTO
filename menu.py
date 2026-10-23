import tkinter as tk
from videopoker import VideoPoker           # aqui vas a traer tu juego desde video_poker.py
# aquí van los imports de los demás juegos, por ejemplo:
# from ruleta import Ruleta. pdd tienes que haber modificado tu juego para poder llamarlo con la plantilla que arme.

JUEGOS = [                                   # para agregar un juego: importarlo y ponerlo aquí
    ("Video Poker", VideoPoker),
    # ("Ruleta", Ruleta),
]


class Casino(tk.Tk):                          # la ventana principal del casino
    def __init__(self):
        super().__init__()
        self.title("Casino")
        self.pantalla_actual = None           # todavía no hay ninguna pantalla
        self.mostrar_menu()                   # al abrir, se muestra el menú

    def cambiar_pantalla(self, nueva):        # quita la pantalla actual y pone la nueva
        if self.pantalla_actual is not None:
            self.pantalla_actual.destroy()
        self.pantalla_actual = nueva
        self.pantalla_actual.pack(padx=20, pady=20)

    def mostrar_menu(self):
        menu = tk.Frame(self)
        tk.Label(menu, text="Casino", font=("Arial", 28, "bold")).pack(pady=20)

        for nombre, ClaseJuego in JUEGOS:    # un botón por cada juego de la lista
            tk.Button(menu, text=nombre, font=("Arial", 16), width=20,
                      command=lambda clase=ClaseJuego: self.mostrar_juego(clase)).pack(pady=5)

        tk.Button(menu, text="Salir", font=("Arial", 14), width=10,
                  command=self.destroy).pack(pady=20)
        self.cambiar_pantalla(menu)

    def mostrar_juego(self, ClaseJuego):     # sirve para CUALQUIER juego
        pantalla = tk.Frame(self)
        ClaseJuego(pantalla).pack()          # crea el juego que le pasaron
        tk.Button(pantalla, text="Volver al menú", font=("Arial", 12),
                  command=self.mostrar_menu).pack(pady=10)
        self.cambiar_pantalla(pantalla)


if __name__ == "__main__":
    app = Casino()
    app.mainloop()
