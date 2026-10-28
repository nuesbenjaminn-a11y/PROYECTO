
import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import os

# ==========================================
# 1. CONFIGURACIÓN Y VARIABLES GLOBALES
# ==========================================
ARCHIVO_RANKING = "ranking.json"
RANGO_MIN = 1
RANGO_MAX = 100
MAX_INTENTOS = 10

# ==========================================
# 2. LÓGICA DE ARCHIVOS (JSON)
# ==========================================
def cargar_ranking():
    """Lee el archivo JSON. Si no existe, retorna una lista vacía."""
    if not os.path.exists(ARCHIVO_RANKING):
        return []
    try:
        with open(ARCHIVO_RANKING, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, IOError):
        return []

def guardar_ranking(lista_ranking):
    """Guarda la lista de jugadores en el archivo JSON."""
    with open(ARCHIVO_RANKING, "w", encoding="utf-8") as archivo:
        json.dump(lista_ranking, archivo, indent=4, ensure_ascii=False)

# ==========================================
# 3. ALGORITMO DE ORDENAMIENTO (BURBUJA)
# ==========================================
def ordenar_ranking_burbuja(lista):
    """
    Ordena la lista de diccionarios de mayor a menor puntaje.
    Implementación manual del algoritmo Bubble Sort.
    """
    n = len(lista)
    for i in range(n):
        for j in range(0, n - i - 1):
            # Comparamos los puntos. Si el actual es menor que el siguiente, los intercambiamos
            if lista[j]["puntos"] < lista[j + 1]["puntos"]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
    return lista

# ==========================================
# 4. INTERFAZ GRÁFICA (TKINTER)
# ==========================================
class JuegoAdivinanza:
    def _init_(self, root):
        self.root = root
        self.root.title("Adivina el Número - Ranking Top 10")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        # Variables del juego
        self.numero_secreto = 0
        self.intentos_restantes = MAX_INTENTOS
        self.nombre_jugador = ""
        self.juego_activo = False

        # Construir la interfaz
        self.crear_widgets()
        self.mostrar_ranking()

    def crear_widgets(self):
        # --- Sección de Inicio ---
        frame_inicio = tk.LabelFrame(self.root, text="Registro de Jugador", padx=10, pady=10)
        frame_inicio.pack(pady=10, padx=10, fill="x")

        tk.Label(frame_inicio, text="Nombre:").pack(side="left")
        self.entry_nombre = tk.Entry(frame_inicio, width=20)
        self.entry_nombre.pack(side="left", padx=5)
        
        self.btn_iniciar = tk.Button(frame_inicio, text="Iniciar Juego", command=self.iniciar_juego, bg="#4CAF50", fg="white")
        self.btn_iniciar.pack(side="left", padx=5)

        # --- Sección de Juego ---
        frame_juego = tk.LabelFrame(self.root, text="Juego", padx=10, pady=10)
        frame_juego.pack(pady=10, padx=10, fill="x")

        self.lbl_mensaje = tk.Label(frame_juego, text="Ingresa tu nombre y presiona Iniciar", font=("Arial", 12))
        self.lbl_mensaje.pack(pady=10)

        self.lbl_intentos = tk.Label(frame_juego, text=f"Intentos restantes: {MAX_INTENTOS}", font=("Arial", 10, "bold"))
        self.lbl_intentos.pack()

        tk.Label(frame_juego, text="Ingresa un número (1-100):").pack(pady=5)
        self.entry_numero = tk.Entry(frame_juego, width=10, font=("Arial", 14), justify="center")
        self.entry_numero.pack(pady=5)
        self.entry_numero.config(state="disabled") # Deshabilitado hasta iniciar

        self.btn_probar = tk.Button(frame_juego, text="Probar Suerte", command=self.probar_intento, state="disabled", bg="#2196F3", fg="white")
        self.btn_probar.pack(pady=10)

        # --- Sección de Ranking ---
        frame_ranking = tk.LabelFrame(self.root, text="🏆 Top 10 Mejores Jugadores", padx=10, pady=10)
        frame_ranking.pack(pady=10, padx=10, fill="both", expand=True)

        # Tabla (Treeview)
        columnas = ("Pos", "Nombre", "Puntos", "Intentos")
        self.tabla = ttk.Treeview(frame_ranking, columns=columnas, show="headings", height=10)
        
        self.tabla.heading("Pos", text="#")
        self.tabla.heading("Nombre", text="Jugador")
        self.tabla.heading("Puntos", text="Puntos")
        self.tabla.heading("Intentos", text="Intentos")

        self.tabla.column("Pos", width=40, anchor="center")
        self.tabla.column("Nombre", width=150, anchor="center")
        self.tabla.column("Puntos", width=80, anchor="center")
        self.tabla.column("Intentos", width=80, anchor="center")

        self.tabla.pack(fill="both", expand=True)

    def iniciar_juego(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Atención", "Por favor, ingresa tu nombre.")
            return

        self.nombre_jugador = nombre
        self.numero_secreto = random.randint(RANGO_MIN, RANGO_MAX)
        self.intentos_restantes = MAX_INTENTOS
        self.juego_activo = True

        # Actualizar UI
        self.entry_nombre.config(state="disabled")
        self.btn_iniciar.config(state="disabled")
        self.entry_numero.config(state="normal")
        self.entry_numero.delete(0, tk.END)
        self.entry_numero.focus()
        self.btn_probar.config(state="normal")
        
        self.actualizar_mensaje(f"¡Hola {self.nombre_jugador}! He pensado un número entre {RANGO_MIN} y {RANGO_MAX}.", "black")
        self.actualizar_intentos()

    def probar_intento(self):
        if not self.juego_activo:
            return

        try:
            intento = int(self.entry_numero.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa un número válido.")
            return

        if intento < RANGO_MIN or intento > RANGO_MAX:
            messagebox.showwarning("Fuera de rango", f"El número debe estar entre {RANGO_MIN} y {RANGO_MAX}.")
            return

        self.intentos_restantes -= 1
        self.actualizar_intentos()
        self.entry_numero.delete(0, tk.END)

        if intento == self.numero_secreto:
            self.ganar()
        elif self.intentos_restantes == 0:
            self.perder()
        elif intento < self.numero_secreto:
            self.actualizar_mensaje("⬆️ El número es MÁS ALTO.", "blue")
        else:
            self.actualizar_mensaje("⬇️ El número es MÁS BAJO.", "red")

    def ganar(self):
        self.juego_activo = False
        self.entry_numero.config(state="disabled")
        self.btn_probar.config(state="disabled")
        
        # Calcular puntaje (más puntos si usa menos intentos)
        intentos_usados = MAX_INTENTOS - self.intentos_restantes
        puntos = (MAX_INTENTOS - intentos_usados) * 100
        
        self.actualizar_mensaje(f"🎉 ¡Felicidades {self.nombre_jugador}! Adivinaste en {intentos_usados} intentos.\nGanaste {puntos} puntos.", "green")
        
        # Guardar en ranking
        self.registrar_puntaje(puntos, intentos_usados)
        self.reiniciar_botones()

    def perder(self):
        self.juego_activo = False
        self.entry_numero.config(state="disabled")
        self.btn_probar.config(state="disabled")
        self.actualizar_mensaje(f"😢 Game Over. El número era {self.numero_secreto}.", "red")
        self.reiniciar_botones()

    def registrar_puntaje(self, puntos, intentos_usados):
        ranking = cargar_ranking()
        nuevo_registro = {
            "nombre": self.nombre_jugador,
            "puntos": puntos,
            "intentos": intentos_usados
        }
        ranking.append(nuevo_registro)
        
        # Ordenar con nuestro algoritmo manual
        ranking_ordenado = ordenar_ranking_burbuja(ranking)
        
        # Guardar solo el Top 10
        top_10 = ranking_ordenado[:10]
        guardar_ranking(top_10)
        
        # Actualizar la tabla visual
        self.mostrar_ranking()

    def mostrar_ranking(self):
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        ranking = cargar_ranking()
        for i, jugador in enumerate(ranking):
            self.tabla.insert("", "end", values=(i+1, jugador["nombre"], jugador["puntos"], jugador["intentos"]))

    def reiniciar_botones(self):
        self.entry_nombre.config(state="normal")
        self.btn_iniciar.config(state="normal")
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.focus()

    def actualizar_mensaje(self, texto, color):
        self.lbl_mensaje.config(text=texto, fg=color)

    def actualizar_intentos(self):
        self.lbl_intentos.config(text=f"Intentos restantes: {self.intentos_restantes}")

# ==========================================
# 5. PUNTO DE ENTRADA
# ==========================================
if _name_ == "_main_":
    root = tk.Tk()
    app = JuegoAdivinanza(root)
    root.mainloop()
