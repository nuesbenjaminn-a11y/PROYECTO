import tkinter as tk
from tkinter import messagebox
import random
import json
import os

racha_actual = 0
ARCHIVO_JSON = "ranking.json"

def guardar_puntaje(nombre, racha):
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

# --- NUEVO: Función con Algoritmo de Ordenamiento Propio ---
def mostrar_ranking():
    if not os.path.exists(ARCHIVO_JSON):
        messagebox.showinfo("Ranking", "Aún no hay puntajes guardados.")
        return

    try:
        with open(ARCHIVO_JSON, "r") as archivo:
            datos = json.load(archivo)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "El archivo de ranking está corrupto.")
        return

    # Algoritmo de Burbuja (Bubble Sort) para ordenar de MAYOR a MENOR
    n = len(datos)
    for i in range(n):
        for j in range(0, n - i - 1):
            # Si el puntaje actual es menor que el siguiente, se intercambian
            if datos[j]['puntaje'] < datos[j + 1]['puntaje']:
                datos[j], datos[j + 1] = datos[j + 1], datos[j]

    # Extraer solo los primeros 10 elementos
    top_10 = datos[:10]

    # Crear una ventana secundaria (Toplevel) para mostrar el Top 10
    ventana_ranking = tk.Toplevel(ventana)
    ventana_ranking.title("Top 10 - Ranking")
    ventana_ranking.geometry("250x350")

    tk.Label(ventana_ranking, text="🏆 TOP 10 JUGADORES 🏆", font=("Arial", 12, "bold")).pack(pady=10)

    # Imprimir los jugadores ordenados en la ventana
    for indice, jugador in enumerate(top_10):
        texto = f"{indice + 1}. {jugador['nombre']} - Racha: {jugador['puntaje']}"
        tk.Label(ventana_ranking, text=texto, font=("Arial", 11)).pack(pady=2)
# -----------------------------------------------------------

def verificar_jugada(eleccion_usuario):
    global racha_actual
    
    nombre = entrada_nombre.get().strip()
    
    if not nombre:
        messagebox.showwarning("Atención", "¡Por favor, ingresa tu nombre antes de jugar!")
        return
        
    eleccion_maquina = random.choice(["Cara", "Cruz"])
    
    if eleccion_usuario == eleccion_maquina:
        racha_actual += 1
        etiqueta_estado.config(text=f"¡Acertaste! Salió {eleccion_maquina}", fg="green")
    else:
        guardar_puntaje(nombre, racha_actual)
        racha_actual = 0
        etiqueta_estado.config(text=f"Fallaste. Salió {eleccion_maquina}", fg="red")
        
    etiqueta_racha.config(text=f"Racha actual: {racha_actual}")

# --- Configuración de la Interfaz ---
ventana = tk.Tk()
ventana.title("Cara o Cruz - Supervivencia")
ventana.geometry("300x380") # Aumentamos la altura para el nuevo botón

marco_nombre = tk.Frame(ventana)
marco_nombre.pack(pady=15)

etiqueta_nombre = tk.Label(marco_nombre, text="Tu nombre:")
etiqueta_nombre.grid(row=0, column=0, padx=5) 

entrada_nombre = tk.Entry(marco_nombre)
entrada_nombre.grid(row=0, column=1, padx=5)  

etiqueta_estado = tk.Label(ventana, text="¿Qué eliges?", font=("Arial", 14))
etiqueta_estado.pack(pady=10)

etiqueta_racha = tk.Label(ventana, text="Racha actual: 0", font=("Arial", 12))
etiqueta_racha.pack(pady=5)

boton_cara = tk.Button(ventana, text="Cara", width=15, command=lambda: verificar_jugada("Cara"))
boton_cara.pack(pady=10)

boton_cruz = tk.Button(ventana, text="Cruz", width=15, command=lambda: verificar_jugada("Cruz"))
boton_cruz.pack(pady=10)

# --- NUEVO: Botón para ver el ranking ---
boton_ranking = tk.Button(ventana, text="Ver Ranking", width=15, bg="gold", command=mostrar_ranking)
boton_ranking.pack(pady=15)
# ----------------------------------------

ventana.mainloop()

etiqueta_estado = tk.Label(ventana, text="¿Qué eliges?", font=("Arial", 14))
etiqueta_estado.pack(pady=10)

etiqueta_racha = tk.Label(ventana, text="Racha actual: 0", font=("Arial", 12))
etiqueta_racha.pack(pady=5)

boton_cara = tk.Button(ventana, text="Cara", width=15, command=lambda: verificar_jugada("Cara"))
boton_cara.pack(pady=10)

boton_cruz = tk.Button(ventana, text="Cruz", width=15, command=lambda: verificar_jugada("Cruz"))
boton_cruz.pack(pady=10)

ventana.mainloop()