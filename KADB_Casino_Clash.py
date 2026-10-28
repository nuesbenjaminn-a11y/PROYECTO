#!/usr/bin/env python3
# main_tk.py
"""
KADB Casino Clash - Hacker Edition (versión mejorada)
- Adivina la carta secreta (1..20). Cada número es un concepto de programación.
- 4 jugadores, 3 minutos.
- Al acertar: la carta se voltea, anillos neón, estrellitas y confeti.
- Terminal con log en vivo + lluvia de código en el encabezado.
- Colección de 20 cartas que se desbloquean (estilo flashcards).
- Ranking Top 10 guardado en JSON y ordenado con un algoritmo PROPIO
  (insertion sort, sin usar sorted() ni list.sort()).
"""
import json
import math
import random
import tkinter as tk
from tkinter import messagebox, font
from pathlib import Path

# ---------------------------------------------------------------- datos
APP_DATA_DIR = Path.home() / ".kadb_casino"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVO_RANKING = APP_DATA_DIR / "ranking.json"
TOP_N = 10

# Tema oscuro neón (tipo editor de código)
P = {
    "fondo": "#0B0F19",
    "panel": "#111827",
    "header": "#0F1524",
    "borde": "#1F2A44",
    "texto": "#C9D1D9",
    "muted": "#6B7A99",
    "verde": "#39FF88",
    "azul": "#58A6FF",
    "naranja": "#FFB454",
    "rojo": "#FF5C7A",
    "gold": "#FFD43B",
    "silver": "#CBD5E1",
    "bronze": "#D97706",
    "morado": "#BD93F9",
    "cyan": "#22D3EE",
    "back_border": "#1F2A44",
}

CARD_COLORS = ["#5EEAD4", "#FB923C", "#F9A8D4", "#F87171",
               "#C4B5FD", "#60A5FA", "#FACC15", "#86EFAC"]
PLAYER_COLORS = ["#5EEAD4", "#FB923C", "#F9A8D4", "#818CF8"]
CONFETTI_COLORS = CARD_COLORS + ["#FFFFFF"]
RAIN_CHARS = "01{}[]()<>/;=+*#$%&@λ"

# (nombre, símbolo que se dibuja en la carta)  -> editable
CARDS = [
    ("variable", "x = 5"), ("función", "f(x)"), ("lista", "[1,2,3]"),
    ("diccionario", "{k: v}"), ("bucle", "for ↻"), ("recursión", "f(f(f))"),
    ("clase", "class"), ("módulo", ".py"), ("import", "import"),
    ("algoritmo", "O(n)"), ("compilador", "gcc"), ("intérprete", ">>>"),
    ("bug", "404"), ("commit", "git +"), ("branch", "main ⑂"),
    ("pull request", "PR #1"), ("stack", "LIFO"), ("heap", "malloc"),
    ("lambda", "λ"), ("decorador", "@"),
]

MONO = "Courier New"  # se ajusta al iniciar según las fuentes disponibles

HEADER_W, HEADER_H = 1096, 56
STAGE_W, STAGE_H = 360, 176
STAGE_CARD_W, STAGE_CARD_H = 120, 132
STAGE_CARD_TOP = 4
STAGE_CY = STAGE_CARD_TOP + STAGE_CARD_H // 2  # centro vertical de la carta


# ---------------------------------------------------------------- ordenamiento propio
def es_mejor(a, b):
    """True si la entrada 'a' debe ir ANTES que 'b' en el ranking.

    Criterios: 1) más puntaje  2) más wins  3) menos intentos.
    """
    if a["puntaje"] != b["puntaje"]:
        return a["puntaje"] > b["puntaje"]
    if a.get("wins", 0) != b.get("wins", 0):
        return a.get("wins", 0) > b.get("wins", 0)
    return a["intentos"] < b["intentos"]


def ordenar_ranking(ranking, limite=TOP_N):
    """Algoritmo de ordenamiento propio: INSERTION SORT.

    Recorre la lista y va insertando cada elemento en su posición correcta
    dentro de la parte ya ordenada. Es estable (los empates totales conservan
    su orden original). Complejidad: O(n²) en el peor caso, O(n) si ya está
    ordenada; suficiente porque el ranking nunca pasa de unas pocas entradas.
    No se usa sorted() ni list.sort().
    """
    lista = list(ranking)  # copia, no modifica la original
    for i in range(1, len(lista)):
        actual = lista[i]
        j = i - 1
        while j >= 0 and es_mejor(actual, lista[j]):
            lista[j + 1] = lista[j]  # desplaza hacia la derecha
            j -= 1
        lista[j + 1] = actual
    return lista[:limite]  # solo el Top N


# ---------------------------------------------------------------- persistencia
def _entrada_valida(d):
    return (isinstance(d, dict)
            and isinstance(d.get("jugador"), str)
            and isinstance(d.get("puntaje"), int)
            and isinstance(d.get("intentos"), int))


def cargar_ranking():
    """Lee el JSON; si no existe, está dañado o tiene entradas raras, las ignora."""
    try:
        with ARCHIVO_RANKING.open("r", encoding="utf-8") as f:
            datos = json.load(f)
    except (OSError, ValueError):
        return []
    if not isinstance(datos, list):
        return []
    return [d for d in datos if _entrada_valida(d)]


def guardar_ranking(ranking):
    """Escritura segura: primero a un archivo temporal y luego se reemplaza."""
    tmp = ARCHIVO_RANKING.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)
    tmp.replace(ARCHIVO_RANKING)


def guardar_resultados_de_partida(resultados):
    """Combina los resultados nuevos con el ranking guardado.

    - Ignora a quien no jugó (0 intentos) para no llenar el ranking de ceros.
    - Guarda solo la MEJOR partida de cada jugador (por nombre).
    - Ordena con el algoritmo propio y se queda con el Top 10.
    """
    nuevos = [r for r in resultados if r["intentos"] > 0]
    mejores = {}
    for r in cargar_ranking() + nuevos:
        clave = r["jugador"].strip().lower()
        entrada = {"jugador": r["jugador"].strip(), "puntaje": r["puntaje"],
                   "intentos": r["intentos"], "wins": r.get("wins", 0)}
        if clave not in mejores or es_mejor(entrada, mejores[clave]):
            mejores[clave] = entrada
    ranking = ordenar_ranking(list(mejores.values()))
    for pos, r in enumerate(ranking, start=1):
        r["id"] = pos
    guardar_ranking(ranking)
    return ranking


def generar_numero(anterior=None):
    """Número secreto 1..20; evita repetir la misma carta dos rondas seguidas."""
    n = random.randint(1, len(CARDS))
    while anterior is not None and n == anterior:
        n = random.randint(1, len(CARDS))
    return n


# ---------------------------------------------------------------- dibujo
def rrect(c, x1, y1, x2, y2, r, **kw):
    """Rectángulo redondeado en un Canvas."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
           x2, y1 + r, x2, y2 - r, x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2,
           x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r,
           x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


def star_points(cx, cy, ro, ri):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = ro if i % 2 == 0 else ri
        pts += [cx + r * math.cos(ang), cy + r * math.sin(ang)]
    return pts


def draw_card(c, cx, top, w, h, idx, revealed, tag, glyph_size, label_size,
              num_size, full_w=None, back_text=None, badge=False):
    """Dibuja una carta estilo flashcard: borde de color, símbolo y etiqueta."""
    full_w = full_w or w
    w = max(w, 4)
    x1, x2 = cx - w / 2, cx + w / 2
    y1, y2 = top, top + h
    color = CARD_COLORS[idx % len(CARD_COLORS)] if revealed else P["back_border"]
    rrect(c, x1, y1, x2, y2, 14, fill=color, outline="", tags=tag)
    inset = min(4, w / 2 - 1)
    rrect(c, x1 + inset, y1 + inset, x2 - inset, y2 - inset, 11,
          fill="#FFFFFF" if revealed else P["panel"], outline="", tags=tag)
    if w < full_w * 0.6:  # durante el giro no dibujamos textos
        return
    nombre, glyph = CARDS[idx]
    if revealed:
        c.create_text(x1 + 10, y1 + 8, text=f"#{idx + 1:02d}", anchor="nw",
                      fill="#94A3B8", font=(MONO, num_size, "bold"), tags=tag)
        c.create_text(cx, y1 + h * 0.42, text=glyph, fill="#0F172A",
                      font=(MONO, glyph_size, "bold"), tags=tag)
        pw = w * 0.84
        py1, py2 = y1 + h * 0.70, y1 + h * 0.89
        rrect(c, cx - pw / 2, py1, cx + pw / 2, py2, 8, fill=color, outline="", tags=tag)
        c.create_text(cx, (py1 + py2) / 2, text=nombre.upper(), fill="#0F172A",
                      font=(MONO, label_size, "bold"), tags=tag)
        if badge:
            c.create_polygon(star_points(x2 - 13, y1 + 13, 7, 3), fill=P["gold"],
                             outline="", tags=tag)
    else:
        txt = back_text if back_text is not None else str(idx + 1)
        c.create_text(cx, (y1 + y2) / 2, text=txt, fill=P["muted"],
                      font=(MONO, glyph_size + 4, "bold"), tags=tag)


# ---------------------------------------------------------------- UI
class PlayerPanel:
    def __init__(self, master, index, on_try, color):
        self.index = index
        self.on_try = on_try
        self.color = color

        self.frame = tk.Frame(master, bg=P["panel"], highlightthickness=2,
                              highlightbackground=color, highlightcolor=color)

        top = tk.Frame(self.frame, bg=P["panel"])
        top.pack(fill="x", padx=10, pady=(8, 2))
        tk.Label(top, text=f"player_{index + 1} =", bg=P["panel"], fg=color,
                 font=(MONO, 11, "bold")).pack(side="left")
        self.entry_nombre = tk.Entry(top, width=12, font=(MONO, 11), bg=P["fondo"],
                                     fg=P["verde"], insertbackground=P["verde"],
                                     disabledbackground=P["fondo"], disabledforeground=P["muted"],
                                     relief="flat")
        self.entry_nombre.insert(0, f"Player{index + 1}")
        self.entry_nombre.pack(side="left", padx=8, ipady=3)

        row = tk.Frame(self.frame, bg=P["panel"])
        row.pack(pady=4)
        tk.Label(row, text="guess(", bg=P["panel"], fg=P["morado"], font=(MONO, 12, "bold")).pack(side="left")
        self.entry_numero = tk.Entry(row, width=4, justify="center", font=(MONO, 14, "bold"),
                                     bg=P["fondo"], fg=P["gold"], insertbackground=P["gold"],
                                     disabledbackground=P["fondo"], disabledforeground=P["muted"],
                                     relief="flat")
        self.entry_numero.pack(side="left", ipady=3, padx=2)
        tk.Label(row, text=")", bg=P["panel"], fg=P["morado"], font=(MONO, 12, "bold")).pack(side="left", padx=(0, 10))
        self.btn_try = tk.Button(row, text="run ▶", command=self._on_try_click, bg=color,
                                 fg="#0B0F19", activebackground="#FFFFFF", relief="flat",
                                 font=(MONO, 11, "bold"), padx=10, cursor="hand2")
        self.btn_try.pack(side="left")
        self.entry_numero.bind("<Return>", lambda e: self._on_try_click())

        self.lbl_feedback = tk.Label(self.frame, text="", bg=P["panel"], fg=P["texto"],
                                     font=(MONO, 10), wraplength=300, justify="center", height=2)
        self.lbl_feedback.pack(pady=(4, 2))

        self.lbl_stats = tk.Label(self.frame, text="", bg=P["panel"], fg=P["muted"], font=(MONO, 10))
        self.lbl_stats.pack()

        self.lbl_stars = tk.Label(self.frame, text="", bg=P["panel"], fg=P["gold"], font=(MONO, 16, "bold"))
        self.lbl_stars.pack(pady=(0, 6))

        self.reset_state()

    # --- estado
    def reset_state(self):
        self.attempts_this_round = 0
        self.total_attempts = 0
        self.total_score = 0
        self.wins = 0
        self.stars = 0
        self.refresh_stats()
        self.lbl_stars.config(text="☆ ☆ ☆", fg=P["borde"])
        self.feedback("")

    def refresh_stats(self):
        self.lbl_stats.config(
            text=f"tries={self.total_attempts}  pts={self.total_score}  wins={self.wins}")

    def _on_try_click(self):
        val = self.entry_numero.get().strip()
        try:
            intento = int(val)
        except ValueError:
            self.feedback("✖ TypeError: número inválido", color=P["rojo"])
            return
        if not (1 <= intento <= len(CARDS)):
            self.feedback(f"✖ IndexError: usa 1-{len(CARDS)}", color=P["rojo"])
            return
        self.on_try(self.index, intento)

    def feedback(self, text, color=None):
        self.lbl_feedback.config(text=text, fg=color or P["texto"])

    def increment_attempt(self):
        self.attempts_this_round += 1
        self.total_attempts += 1
        self.refresh_stats()

    def add_score(self, pts):
        self.total_score += pts
        self.refresh_stats()

    def add_star(self):
        self.stars += 1
        txt = "★" * min(self.stars, 10)
        if self.stars > 10:
            txt += f" x{self.stars}"
        self.lbl_stars.config(text=txt)
        self._pulse(0)

    def _pulse(self, n):
        if n >= 6:
            self.lbl_stars.config(fg=P["gold"])
            return
        self.lbl_stars.config(fg="#FFFFFF" if n % 2 == 0 else P["gold"])
        self.frame.after(90, lambda: self._pulse(n + 1))

    def set_playing(self, playing):
        st_game = "normal" if playing else "disabled"
        st_name = "disabled" if playing else "normal"
        self.btn_try.config(state=st_game)
        self.entry_numero.config(state=st_game)
        self.entry_nombre.config(state=st_name)

    def clear_inputs(self):
        self.entry_numero.delete(0, tk.END)

    def get_name(self):
        return self.entry_nombre.get().strip()[:12] or f"Player{self.index + 1}"


class CasinoMultiplayer:
    def __init__(self, root):
        self.root = root
        self.root.title("main.py — KADB Casino Clash")
        self.root.configure(bg=P["fondo"])
        self.root.resizable(False, False)

        self.secret = generar_numero()
        self.round_number = 1
        self.match_duration = 3 * 60
        self.time_left = self.match_duration
        self.match_running = False
        self.collected = set()
        self.rank_win = None

        self._timer_id = None
        self._fx_job = None
        self._flip_job = None
        self._idle_job = None
        self._caption_job = None
        self._cursor_on = True
        self.fx = []
        self.rain = []

        self.crear_ui()

        self.players = []
        for i in range(4):
            p = PlayerPanel(self.players_frame, i, self.on_player_try, PLAYER_COLORS[i])
            p.frame.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="nsew")
            p.set_playing(False)
            self.players.append(p)

        self.show_idle_stage()
        self.redraw_collection()
        self.boot_log()
        self._blink_cursor()
        self._rain_step()
        self._centrar_ventana()

    def _centrar_ventana(self):
        """Ajusta la ventana a su contenido y la deja arriba/centrada para que no tape la barra de tareas."""
        self.root.update_idletasks()
        w, h = self.root.winfo_reqwidth(), self.root.winfo_reqheight()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h - 80) // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ------------------------------------------------ construcción de la UI
    def crear_ui(self):
        # ---- encabezado estilo IDE (con lluvia de código)
        self.header = tk.Canvas(self.root, width=HEADER_W, height=HEADER_H, bg=P["header"],
                                highlightthickness=1, highlightbackground=P["borde"])
        self.header.pack(padx=12, pady=(6, 4))
        h = self.header

        for i in range(0, HEADER_W, 16):
            n = random.randint(4, 7)
            txt = "\n".join(random.choice(RAIN_CHARS) for _ in range(n))
            tid = h.create_text(i + 8, random.randint(-80, HEADER_H), text=txt, anchor="n",
                                fill="#14452C", font=(MONO, 8), tags="rain")
            self.rain.append({"id": tid, "speed": random.uniform(1, 3)})

        f_title = font.Font(family=MONO, size=15, weight="bold")
        f_sub = font.Font(family=MONO, size=9)
        tokens = [("kadb_casino_clash", P["verde"]), ("()", P["texto"]), (":", P["texto"])]
        title_w = sum(f_title.measure(t) for t, _ in tokens)
        sub = "# adivina la carta de programación · 4 jugadores · 3 min · rango 1-20"
        sub_w = f_sub.measure(sub)
        box_r = 90 + max(title_w + f_title.measure("█"), sub_w) + 14
        h.create_rectangle(82, 4, box_r, HEADER_H - 4, fill=P["header"], outline="")

        for cx, col in ((24, "#FF5F56"), (46, "#FFBD2E"), (68, "#27C93F")):
            h.create_oval(cx - 6, 22, cx + 6, 34, fill=col, outline="")

        x = 90
        for text, col in tokens:
            h.create_text(x, 20, text=text, anchor="w", fill=col, font=f_title)
            x += f_title.measure(text)
        h.create_text(x, 20, text="█", anchor="w", fill=P["verde"], font=f_title, tags="cursor")
        h.create_text(90, 42, text=sub, anchor="w", fill="#6A9955", font=f_sub)

        h.create_rectangle(HEADER_W - 110, 14, HEADER_W - 8, 42, fill=P["header"], outline="")
        h.create_text(HEADER_W - 14, 28, text="● main.py", anchor="e",
                      fill=P["cyan"], font=(MONO, 10, "bold"))

        # ---- zona central
        middle = tk.Frame(self.root, bg=P["fondo"], height=404)
        middle.pack(fill="x", padx=12)
        middle.pack_propagate(False)

        self.players_frame = tk.Frame(middle, bg=P["fondo"])
        self.players_frame.pack(side="left", fill="both", expand=True)
        for i in range(2):
            self.players_frame.grid_rowconfigure(i, weight=1)
            self.players_frame.grid_columnconfigure(i, weight=1)

        right = tk.Frame(middle, bg=P["panel"], width=380, highlightthickness=1,
                         highlightbackground=P["borde"])
        right.pack(side="right", fill="y", padx=(12, 0))
        right.pack_propagate(False)

        self.lbl_timer = tk.Label(right, text="03:00", bg=P["panel"], fg=P["verde"],
                                  font=(MONO, 24, "bold"))
        self.lbl_timer.pack(pady=(2, 0))
        self.lbl_round = tk.Label(right, text="round = 1", bg=P["panel"], fg=P["muted"], font=(MONO, 10))
        self.lbl_round.pack()

        btns = tk.Frame(right, bg=P["panel"])
        btns.pack(pady=3)
        self.btn_start = tk.Button(btns, text="▶ run (3 min)", command=self.start_match,
                                   bg=P["verde"], fg="#0B0F19", relief="flat",
                                   font=(MONO, 10, "bold"), padx=8, cursor="hand2")
        self.btn_start.pack(side="left", padx=3)
        self.btn_reset = tk.Button(btns, text="↺ reset", command=self.reset_match,
                                   bg=P["borde"], fg=P["texto"], relief="flat",
                                   font=(MONO, 10, "bold"), padx=8, cursor="hand2")
        self.btn_reset.pack(side="left", padx=3)
        self.btn_rank = tk.Button(btns, text="★ top10", command=self.mostrar_ranking,
                                  bg=P["gold"], fg="#0B0F19", relief="flat",
                                  font=(MONO, 10, "bold"), padx=8, cursor="hand2")
        self.btn_rank.pack(side="left", padx=3)

        # escenario: aquí se voltea la carta y aparecen anillos, estrellas y confeti
        self.stage = tk.Canvas(right, width=STAGE_W, height=STAGE_H, bg=P["panel"], highlightthickness=0)
        self.stage.pack(pady=(0, 4))
        for gx in range(10, STAGE_W, 20):          # cuadrícula de puntos tipo editor
            for gy in range(8, STAGE_H, 20):
                self.stage.create_oval(gx, gy, gx + 2, gy + 2, fill="#1A2338", outline="", tags="bg")

        tk.Label(right, text="▌terminal", bg=P["panel"], fg=P["muted"], font=(MONO, 9, "bold"),
                 anchor="w").pack(fill="x", padx=10)
        term_frame = tk.Frame(right, bg=P["fondo"])
        term_frame.pack(padx=8, pady=(0, 8), fill="x")
        self.term = tk.Text(term_frame, width=48, height=6, font=(MONO, 9), bg=P["fondo"],
                            fg=P["texto"], bd=0, highlightthickness=0, wrap="none",
                            state="disabled", cursor="arrow", padx=6, pady=4)
        self.term.pack(side="left", fill="x", expand=True)
        for tag, col in (("ok", P["verde"]), ("info", P["azul"]), ("warn", P["naranja"]),
                         ("err", P["rojo"]), ("dim", P["muted"]), ("cmd", P["morado"]),
                         ("star", P["gold"])):
            self.term.tag_config(tag, foreground=col)

        # colección de cartas
        self.lbl_collection = tk.Label(self.root, text="", bg=P["fondo"], fg=P["azul"],
                                       font=(MONO, 10, "bold"), anchor="w")
        self.lbl_collection.pack(fill="x", padx=14, pady=(4, 0))
        self.collect_canvas = tk.Canvas(self.root, width=1096, height=122, bg=P["fondo"], highlightthickness=0)
        self.collect_canvas.pack(padx=12)

    # ------------------------------------------------ animaciones del encabezado
    def _blink_cursor(self):
        self._cursor_on = not self._cursor_on
        self.header.itemconfigure("cursor", fill=P["verde"] if self._cursor_on else P["header"])
        self.root.after(500, self._blink_cursor)

    def _rain_step(self):
        h = self.header
        for r in self.rain:
            h.move(r["id"], 0, r["speed"])
            x, y = h.coords(r["id"])
            if y > HEADER_H + 4:
                n = random.randint(4, 7)
                h.itemconfigure(r["id"], text="\n".join(random.choice(RAIN_CHARS) for _ in range(n)))
                h.coords(r["id"], x, -70)
        self.root.after(70, self._rain_step)

    # ------------------------------------------------ terminal
    def log(self, text, tag="dim"):
        t = self.term
        t.config(state="normal")
        t.insert(tk.END, text + "\n", tag)
        if int(t.index("end-1c").split(".")[0]) > 300:
            t.delete("1.0", "50.0")
        t.see(tk.END)
        t.config(state="disabled")

    def clear_log(self):
        self.term.config(state="normal")
        self.term.delete("1.0", tk.END)
        self.term.config(state="disabled")

    def ts(self):
        m, s = divmod(max(self.time_left, 0), 60)
        return f"[{m:02d}:{s:02d}]"

    def boot_log(self):
        self.clear_log()
        self.log("> listo. pulsa run para empezar", "ok")
        self.actualizar_ranking_display()

    # ------------------------------------------------ colección
    def redraw_collection(self):
        c = self.collect_canvas
        c.delete("all")
        for i in range(len(CARDS)):
            col, row = i % 10, i // 10
            cx = 2 + col * 110 + 50
            top = 2 + row * 60
            draw_card(c, cx, top, 100, 56, i, i in self.collected, "mini",
                      glyph_size=10, label_size=6, num_size=6, badge=True)
        self.lbl_collection.config(
            text=f"colección.json  —  {len(self.collected)}/{len(CARDS)} cartas desbloqueadas")

    # ------------------------------------------------ escenario
    def _draw_stage_card(self, w, idx, revealed):
        c = self.stage
        c.delete("card")
        draw_card(c, STAGE_W / 2, STAGE_CARD_TOP, w, STAGE_CARD_H, idx, revealed, "card",
                  glyph_size=20, label_size=9, num_size=9, full_w=STAGE_CARD_W, back_text="?")
        c.tag_raise("fx")

    def _cancel(self, attr):
        job = getattr(self, attr)
        if job is not None:
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
            setattr(self, attr, None)

    def show_idle_stage(self):
        self._cancel("_idle_job")
        self._cancel("_caption_job")
        self.stage.delete("caption")
        self._draw_stage_card(STAGE_CARD_W, 0, False)
        self.stage.create_text(STAGE_W / 2, STAGE_H - 12, text=f"secret = ?   # 1..{len(CARDS)}",
                               fill=P["muted"], font=(MONO, 10, "bold"), tags="caption")

    def set_caption(self, text, color=None):
        self.stage.delete("caption")
        self.stage.create_text(STAGE_W / 2, STAGE_H - 12, text=text, fill=color or P["gold"],
                               font=(MONO, 10, "bold"), tags="caption")
        self.stage.tag_raise("fx")

    def reveal_card(self, idx, who, pts):
        """Voltea la carta secreta y lanza anillos + estrellas + confeti."""
        self._cancel("_flip_job")
        self._cancel("_idle_job")
        self.stage.delete("caption")
        n = 8

        def step(i):
            if i <= n:
                s, revealed = 1 - i / n, False
            else:
                s, revealed = (i - n) / n, True
            self._draw_stage_card(STAGE_CARD_W * max(s, 0.03), idx, revealed)
            if i < 2 * n:
                self._flip_job = self.root.after(22, lambda: step(i + 1))
            else:
                self._flip_job = None
                self.collected.add(idx)
                self.redraw_collection()
                color = CARD_COLORS[idx % len(CARD_COLORS)]
                self.spawn_ring(color)
                self.root.after(140, lambda: self.spawn_ring("#FFFFFF"))
                self.spawn_confetti(80)
                self.spawn_stars(9)
                self.set_caption(f"★ {who[:12]} +{pts} pts · {CARDS[idx][0]}")
                self._idle_job = self.root.after(3200, self.show_idle_stage)

        step(0)

    # ------------------------------------------------ efectos (anillos + confeti + estrellas)
    def spawn_ring(self, color):
        c = self.stage
        cx, cy = STAGE_W / 2, STAGE_CARD_TOP + STAGE_CARD_H / 2
        pid = c.create_oval(cx - 20, cy - 20, cx + 20, cy + 20, outline=color, width=3, tags="fx")
        self.fx.append({"id": pid, "kind": "ring", "cx": cx, "cy": cy, "r": 20, "life": 22})
        self._start_fx()

    def spawn_confetti(self, amount=80):
        c = self.stage
        for k in range(amount):
            color = random.choice(CONFETTI_COLORS)
            size = random.randint(4, 8)
            if k % 5 < 3:  # explosión desde el centro
                x, y = STAGE_W / 2, STAGE_CY
                vx, vy = random.uniform(-6, 6), random.uniform(-9, -2)
            else:          # lluvia desde arriba
                x, y = random.randint(0, STAGE_W), random.randint(-10, 10)
                vx, vy = random.uniform(-1.5, 1.5), random.uniform(1, 3.5)
            if random.random() < 0.5:
                pid = c.create_rectangle(x, y, x + size, y + size, fill=color, outline="", tags="fx")
            else:
                pid = c.create_oval(x, y, x + size, y + size, fill=color, outline="", tags="fx")
            self.fx.append({"id": pid, "vx": vx, "vy": vy, "g": 0.2, "life": random.randint(70, 110)})
        self._start_fx()

    def spawn_stars(self, amount=8):
        c = self.stage
        for _ in range(amount):
            ro = random.randint(9, 16)
            pid = c.create_polygon(star_points(STAGE_W / 2, STAGE_CY, ro, ro * 0.45), fill=P["gold"],
                                   outline="#F59E0B", tags="fx")
            ang = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 7)
            self.fx.append({"id": pid, "vx": math.cos(ang) * speed, "vy": math.sin(ang) * speed - 2,
                            "g": 0.15, "life": random.randint(40, 65)})
        self._start_fx()

    def _start_fx(self):
        if self._fx_job is None:
            self._fx_job = self.root.after(30, self._fx_step)

    def _fx_step(self):
        c = self.stage
        alive = []
        for p in self.fx:
            if p.get("kind") == "ring":
                p["r"] += 7
                p["life"] -= 1
                r = p["r"]
                if p["life"] <= 0:
                    c.delete(p["id"])
                else:
                    c.coords(p["id"], p["cx"] - r, p["cy"] - r, p["cx"] + r, p["cy"] + r)
                    alive.append(p)
                continue
            c.move(p["id"], p["vx"], p["vy"])
            p["vy"] += p["g"]
            p["life"] -= 1
            coords = c.coords(p["id"])
            if p["life"] <= 0 or not coords or coords[1] > STAGE_H + 20:
                c.delete(p["id"])
            else:
                alive.append(p)
        self.fx = alive
        if self.fx:
            self._fx_job = self.root.after(30, self._fx_step)
        else:
            self._fx_job = None

    def clear_fx(self):
        self._cancel("_fx_job")
        self._cancel("_flip_job")
        self.fx = []
        self.stage.delete("fx")

    # ------------------------------------------------ lógica del juego
    def on_player_try(self, player_index, intento):
        if not self.match_running:
            self.players[player_index].feedback("La partida no está en curso. Pulsa run.", color=P["rojo"])
            return
        player = self.players[player_index]
        name = player.get_name()[:10]
        player.increment_attempt()
        player.clear_inputs()

        if intento == self.secret:
            idx = self.secret - 1
            pts = max(5, 20 - (player.attempts_this_round - 1) * 2)
            player.add_score(pts)
            player.wins += 1
            player.refresh_stats()
            player.add_star()
            player.feedback(f"✔ ¡Acierto! +{pts} pts · {CARDS[idx][0]}", color=P["verde"])
            self.log(f"{self.ts()} {name} ✔ {CARDS[idx][0]} +{pts}pts ★", "star")
            self.reveal_card(idx, player.get_name(), pts)

            self.round_number += 1
            self.lbl_round.config(text=f"round = {self.round_number}")
            self.secret = generar_numero(self.secret)
            for p in self.players:
                p.attempts_this_round = 0
                if p is not player:
                    p.feedback("// nueva carta, ¡a adivinar!", color=P["muted"])
        elif intento < self.secret:
            player.feedback("▲ Mayor", color=P["azul"])
            self.log(f"{self.ts()} {name} guess({intento}) ▲ mayor", "info")
        else:
            player.feedback("▼ Menor", color=P["naranja"])
            self.log(f"{self.ts()} {name} guess({intento}) ▼ menor", "warn")

    def _reset_players(self):
        for p in self.players:
            p.reset_state()

    def start_match(self):
        if self.match_running:
            return
        # Los nombres deben ser distintos: el ranking guarda la mejor partida por nombre.
        nombres = [p.get_name().lower() for p in self.players]
        if len(set(nombres)) < len(nombres):
            messagebox.showwarning("Nombres repetidos",
                                   "Cada jugador debe tener un nombre distinto.")
            return
        self._cancel("_timer_id")
        self.clear_fx()
        self._reset_players()
        self.collected = set()
        self.redraw_collection()
        for p in self.players:
            p.set_playing(True)
        self.secret = generar_numero()
        self.round_number = 1
        self.lbl_round.config(text="round = 1")
        self.time_left = self.match_duration
        self.match_running = True
        self.btn_start.config(state="disabled")
        self.show_idle_stage()
        self.clear_log()
        self.log("$ python main.py --time 180", "cmd")
        self.log("> partida iniciada, ¡suerte!", "ok")
        self._tick_timer()

    def _tick_timer(self):
        if not self.match_running:
            return
        m, s = divmod(max(self.time_left, 0), 60)
        self.lbl_timer.config(text=f"{m:02d}:{s:02d}", fg=P["rojo"] if self.time_left <= 10 else P["verde"])
        if self.time_left <= 0:
            self.end_match()
            return
        self.time_left -= 1
        self._timer_id = self.root.after(1000, self._tick_timer)

    def end_match(self):
        self._cancel("_timer_id")
        self.match_running = False
        self.btn_start.config(state="normal")
        for p in self.players:
            p.set_playing(False)

        resultados = [{"jugador": p.get_name(), "puntaje": p.total_score,
                       "intentos": p.total_attempts, "wins": p.wins} for p in self.players]
        try:
            ranking = guardar_resultados_de_partida(resultados)
        except OSError as e:
            ranking = ordenar_ranking(cargar_ranking())
            messagebox.showerror("Error al guardar", f"No se pudo guardar el ranking:\n{e}")

        best = max((p.wins, p.total_score) for p in self.players)
        winners = [p for p in self.players if (p.wins, p.total_score) == best]
        if best[0] == 0:
            msg = "Nadie acertó esta vez. ¡Revancha!"
            short = "GAME OVER · nadie acertó"
        elif len(winners) > 1:
            names = ", ".join(w.get_name() for w in winners)
            msg = f"Empate entre: {names}\nWins: {best[0]} — Puntaje: {best[1]}"
            short = "GAME OVER · empate"
        else:
            w = winners[0]
            msg = f"Ganador: {w.get_name()}\nWins: {w.wins} — Puntaje: {w.total_score}"
            short = f"GAME OVER · gana {w.get_name()[:12]}"

        self.log("> fin de la partida (exit 0)", "warn")
        self.actualizar_ranking_display(ranking)

        self.show_idle_stage()
        if best[0] > 0:
            self.spawn_ring(P["verde"])
            self.spawn_confetti(160)
            self.spawn_stars(14)
        self.set_caption(f"★ {short} ★")
        self.root.after(1300, lambda: self._dialogo_final(msg))

    def _dialogo_final(self, msg):
        messagebox.showinfo("Fin de la partida", msg)
        self.mostrar_ranking()

    def reset_match(self):
        self._cancel("_timer_id")
        self.match_running = False
        self.btn_start.config(state="normal")
        self.lbl_timer.config(text="03:00", fg=P["verde"])
        self.secret = generar_numero()
        self.round_number = 1
        self.lbl_round.config(text="round = 1")
        self.collected = set()
        self.clear_fx()
        self._reset_players()
        for p in self.players:
            p.set_playing(False)
        self.show_idle_stage()
        self.redraw_collection()
        self.boot_log()

    # ------------------------------------------------ ranking
    def actualizar_ranking_display(self, ranking=None):
        """Muestra el podio (top 3) en la terminal. El Top 10 completo está en el botón ★ top10."""
        if ranking is None:
            ranking = ordenar_ranking(cargar_ranking())
        self.log("$ cat ranking.json | head -3", "cmd")
        if not ranking:
            self.log("// aún no hay puntajes", "dim")
            return
        for i, item in enumerate(ranking[:3], start=1):
            tag = "star" if i == 1 else "info"
            self.log(f"{i:>2}. {item['jugador'][:10]:10} {item['puntaje']:>4}p "
                     f"{item.get('wins', 0):>2}w {item['intentos']:>3}i", tag)

    def mostrar_ranking(self):
        """Ventana con el Top 10 completo (ordenado con el insertion sort propio)."""
        if self.rank_win is not None and self.rank_win.winfo_exists():
            self.rank_win.destroy()
        ranking = ordenar_ranking(cargar_ranking())

        win = tk.Toplevel(self.root)
        self.rank_win = win
        win.title("ranking.json — Top 10")
        win.configure(bg=P["panel"])
        win.resizable(False, False)
        win.transient(self.root)

        tk.Label(win, text="★ TOP 10 ★", bg=P["panel"], fg=P["gold"],
                 font=(MONO, 16, "bold")).grid(row=0, column=0, columnspan=5, pady=(14, 8), padx=20)

        for c, (txt, w) in enumerate((("#", 3), ("jugador", 14), ("pts", 6), ("wins", 5), ("tries", 6))):
            tk.Label(win, text=txt, bg=P["panel"], fg=P["muted"], width=w,
                     font=(MONO, 10, "bold")).grid(row=1, column=c, padx=4)

        if not ranking:
            tk.Label(win, text="// aún no hay puntajes. ¡Juega una partida!", bg=P["panel"],
                     fg=P["muted"], font=(MONO, 10)).grid(row=2, column=0, columnspan=5, pady=20)
        podio = [P["gold"], P["silver"], P["bronze"]]
        for r, item in enumerate(ranking):
            col = podio[r] if r < 3 else P["texto"]
            valores = (str(r + 1), item["jugador"][:14], str(item["puntaje"]),
                       str(item.get("wins", 0)), str(item["intentos"]))
            for c, (val, w) in enumerate(zip(valores, (3, 14, 6, 5, 6))):
                tk.Label(win, text=val, bg=P["panel"], fg=col, width=w,
                         font=(MONO, 11, "bold" if r < 3 else "normal"),
                         anchor="w" if c == 1 else "center").grid(row=r + 2, column=c, padx=4, pady=1)

        tk.Button(win, text="cerrar", command=win.destroy, bg=P["borde"], fg=P["texto"],
                  relief="flat", font=(MONO, 10, "bold"), padx=14,
                  cursor="hand2").grid(row=14, column=0, columnspan=5, pady=14)


def elegir_fuente_mono(root):
    disponibles = set(font.families(root))
    for f in ("Consolas", "JetBrains Mono", "Menlo", "DejaVu Sans Mono", "Courier New"):
        if f in disponibles:
            return f
    return "Courier"


if __name__ == "__main__":
    root = tk.Tk()
    MONO = elegir_fuente_mono(root)
    app = CasinoMultiplayer(root)
    root.mainloop()


