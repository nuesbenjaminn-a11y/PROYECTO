# =====================================================================
# CARA O CRUZ 
# ---------------------------------------------------------------------
# CAMBIOS PARA PODER USARLO DESDE EL MENÚ PRINCIPAL (menu.py):
#
# 1. El archivo se llamaba "prueba de cara o cruz.py". Se cambió a
#    "cara_o_cruz.py" porque Python NO puede hacer import de un archivo
#    que tiene espacios en el nombre.
#
# 2. Antes el juego estaba hecho con funciones sueltas y variables
#    globales, y creaba su propia ventana con tk.Tk() apenas se abría
#    el archivo. Eso hacía que, al importarlo desde menu.py, se abriera
#    una segunda ventana aparte y el menú no pudiera controlarlo.
#
# 3. Ahora todo el juego es una CLASE (CaraOCruz) que hereda de
#    tk.Frame, siguiendo la plantilla del README. Un Frame es como una
#    "caja" que se puede meter dentro de cualquier ventana. Así el menú
#    crea la caja del juego dentro de SU ventana, y la puede quitar
#    cuando el jugador presiona "Volver al menú".
#
# 4. Se borró el código repetido que estaba después del mainloop()
#    (las etiquetas y botones estaban escritos dos veces).
# =====================================================================


import tkinter as tk
from tkinter import messagebox
import random
import json
import os

# CAMBIO: se borró "racha_actual = 0" de aquí arriba. Ya no es una
# variable global; ahora vive dentro de la clase como self.racha_actual.
ARCHIVO_JSON = "ranking.json"


def guardar_puntaje(nombre, racha):          # se queda afuera: no usa widgets
    if racha == 0:
        return

    datos = []
    if os.path.exists(ARCHIVO_JSON):
        try:
            with open(ARCHIVO_JSON, "r") as archivo:
                datos = json.load(archivo)
        except json.JSONDecodeError:
            datos = []

    datos.append({"nombre": nombre, "puntaje": racha})

    with open(ARCHIVO_JSON, "w") as archivo:
        json.dump(datos, archivo, indent=4)

    messagebox.showinfo("Guardado", f"Puntaje de {racha} guardado correctamente.")


class CaraOCruz(tk.Frame):                   # el juego es un Frame (plantilla del README)
    def __init__(self, master=None):
        super().__init__(master)
        self.racha_actual = 0                # antes era variable global

        # --- Configuración de la Interfaz ---
        marco_nombre = tk.Frame(self)
        marco_nombre.pack(pady=15)

        etiqueta_nombre = tk.Label(marco_nombre, text="Tu nombre:")
        etiqueta_nombre.grid(row=0, column=0, padx=5)
        #SELF?
        # "self" es el propio juego. Todo lo que se guarda como
        # self.algo le pertenece al juego y se puede usar desde
        # CUALQUIER método de la clase (verificar_jugada, mostrar_ranking).
        # Una variable SIN self solo existe dentro de la función donde
        # se creó y desaparece cuando esa función termina.
        # CAMBIO: antes era la variable global "racha_actual".
        # Con self ya no hace falta escribir "global racha_actual".
        self.entrada_nombre = tk.Entry(marco_nombre)
        self.entrada_nombre.grid(row=0, column=1, padx=5)

        self.etiqueta_estado = tk.Label(self, text="¿Qué eliges?", font=("Arial", 14))
        self.etiqueta_estado.pack(pady=10)

        self.etiqueta_racha = tk.Label(self, text="Racha actual: 0", font=("Arial", 12))
        self.etiqueta_racha.pack(pady=5)

        boton_cara = tk.Button(self, text="Cara", width=15,
                               command=lambda: self.verificar_jugada("Cara"))
        boton_cara.pack(pady=10)

        boton_cruz = tk.Button(self, text="Cruz", width=15,
                               command=lambda: self.verificar_jugada("Cruz"))
        boton_cruz.pack(pady=10)

        boton_ranking = tk.Button(self, text="Ver Ranking", width=15, bg="gold",
                                  command=self.mostrar_ranking)
        boton_ranking.pack(pady=15)

    def verificar_jugada(self, eleccion_usuario):
        nombre = self.entrada_nombre.get().strip()

        if not nombre:
            messagebox.showwarning("Atención", "¡Por favor, ingresa tu nombre antes de jugar!")
            return

        eleccion_maquina = random.choice(["Cara", "Cruz"])

        if eleccion_usuario == eleccion_maquina:
            self.racha_actual += 1
            self.etiqueta_estado.config(text=f"¡Acertaste! Salió {eleccion_maquina}", fg="green")
        else:
            guardar_puntaje(nombre, self.racha_actual)
            self.racha_actual = 0
            self.etiqueta_estado.config(text=f"Fallaste. Salió {eleccion_maquina}", fg="red")

        self.etiqueta_racha.config(text=f"Racha actual: {self.racha_actual}")

    # Algoritmo de ordenamiento propio (burbuja) para el Top 10
    def mostrar_ranking(self):
        if not os.path.exists(ARCHIVO_JSON):
            messagebox.showinfo("Ranking", "Aún no hay puntajes guardados.")
            return

        try:
            with open(ARCHIVO_JSON, "r") as archivo:
                datos = json.load(archivo)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "El archivo de ranking está corrupto.")
            return

        # Bubble Sort de MAYOR a MENOR
        n = len(datos)
        for i in range(n):
            for j in range(0, n - i - 1):
                if datos[j]["puntaje"] < datos[j + 1]["puntaje"]:
                    datos[j], datos[j + 1] = datos[j + 1], datos[j]

        top_10 = datos[:10]

        ventana_ranking = tk.Toplevel(self)      # antes era tk.Toplevel(ventana)
        ventana_ranking.title("Top 10 - Ranking")
        ventana_ranking.geometry("250x350")

        tk.Label(ventana_ranking, text="🏆 TOP 10 JUGADORES 🏆",
                 font=("Arial", 12, "bold")).pack(pady=10)

        for indice, jugador in enumerate(top_10):
            texto = f"{indice + 1}. {jugador['nombre']} - Racha: {jugador['puntaje']}"
            tk.Label(ventana_ranking, text=texto, font=("Arial", 11)).pack(pady=2)


if __name__ == "__main__":                   # solo corre si se abre este archivo directamente
    ventana = tk.Tk()
    ventana.title("Cara o Cruz - Supervivencia")
    CaraOCruz(ventana).pack(padx=20, pady=20)
    ventana.mainloop()



