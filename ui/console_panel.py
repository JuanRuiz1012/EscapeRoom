import tkinter as tk
from datetime import datetime


BG      = "#050508"
SURFACE = "#0a0a12"
BORDER  = "#1a1a2e"
MUTED   = "#4a4a6a"

# Colores por tipo de mensaje
MSG_COLORS = {
    "expand":  "#3b82f6",   # azul  — expansión normal
    "locked":  "#ef4444",   # rojo  — nodo bloqueado encontrado
    "unlock":  "#22c55e",   # verde — nodo desbloqueado
    "puzzle":  "#a855f7",   # púrpura — pasos del puzzle
    "info":    "#f59e0b",   # ámbar — info general
    "success": "#22c55e",   # verde — meta alcanzada
    "warn":    "#f97316",   # naranja
}

PREFIX = {
    "expand":  "▸ ",
    "locked":  "⚠ ",
    "unlock":  "✓ ",
    "puzzle":  "◈ ",
    "info":    "· ",
    "success": "★ ",
    "warn":    "! ",
}


class ConsolePanel(tk.Frame):
    """
    Consola de ejecución con mensajes coloreados.

    API:
        console.log(msg_type, text)
        console.clear()
        console.log_expand(node_id, path=None)
        console.log_locked(node_id)
        console.log_unlock(node_id)
        console.log_puzzle_step(node_id)
        console.log_puzzle_solved(node_id)
        console.log_goal_reached(node_id)
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._build()

    # API pública

    def log(self, msg_type: str, text: str):
        """Agrega una línea al log. msg_type ∈ MSG_COLORS."""
        color  = MSG_COLORS.get(msg_type, MUTED)
        prefix = PREFIX.get(msg_type, "  ")
        ts     = datetime.now().strftime("%H:%M:%S")

        self._text.configure(state="normal")

        # timestamp
        self._text.insert("end", f"[{ts}] ", "ts")
        # prefijo + mensaje
        tag = f"col_{msg_type}"
        if tag not in self._text.tag_names():
            self._text.tag_configure(tag, foreground=color,
                                     font=("Courier", 10, "bold"))
        self._text.insert("end", prefix, tag)
        self._text.insert("end", text + "\n", tag)

        self._text.configure(state="disabled")
        self._text.see("end")

    def clear(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")
        self.log("info", "Consola limpiada.")

    # Helpers semánticos

    def log_expand(self, node_id: str, path: list = None):
        path_str = f"  [{' → '.join(path)}]" if path else ""
        self.log("expand", f"Expandiendo nodo {{{node_id}}}{path_str}")

    def log_locked(self, node_id: str):
        self.log("locked", f"Nodo bloqueado encontrado: {{{node_id}}}")
        self.log("info",   f"Iniciando búsqueda informada para el puzzle en {{{node_id}}}")

    def log_unlock(self, node_id: str):
        self.log("unlock", f"Puzzle resuelto — desbloqueando nodo {{{node_id}}}")

    def log_puzzle_step(self, node_id: str):
        self.log("puzzle", f"Expandiendo nodo puzzle {{{node_id}}}")

    def log_puzzle_solved(self, goal_node: str):
        self.log("unlock", f"Meta del puzzle alcanzada: {{{goal_node}}}")

    def log_goal_reached(self, node_id: str):
        self.log("success", f"¡META GLOBAL ALCANZADA en {{{node_id}}}! 🎉")

    def log_info(self, text: str):
        self.log("info", text)

    # Construcción

    def _build(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Header
        header = tk.Frame(self, bg=SURFACE, pady=6, padx=10)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        tk.Label(header, text="EXECUTION LOG", bg=SURFACE,
                 fg=MUTED, font=("Courier", 9, "bold"),
                 anchor="w").grid(row=0, column=0, sticky="w")

        tk.Button(header, text="clear", bg=SURFACE, fg=MUTED,
                  activebackground="#1a1a2e", activeforeground="#ffffff",
                  font=("Courier", 8), bd=0, padx=6, pady=2,
                  cursor="hand2", command=self.clear).grid(row=0, column=1)

        tk.Frame(self, bg=BORDER, height=1).grid(row=0, column=0, sticky="sew")

        # Texto scrollable
        text_frame = tk.Frame(self, bg=BG)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self._text = tk.Text(
            text_frame,
            bg=BG, fg=MUTED,
            font=("Courier", 10),
            state="disabled",
            wrap="word",
            relief="flat",
            bd=0,
            padx=10, pady=8,
            selectbackground="#1a1a3a",
            insertbackground="#ffffff",
            cursor="arrow",
        )
        self._text.grid(row=0, column=0, sticky="nsew")
        self._text.tag_configure("ts", foreground="#2a2a4a",
                                  font=("Courier", 9))

        scrollbar = tk.Scrollbar(text_frame, command=self._text.yview,
                                  bg=SURFACE, troughcolor=BG,
                                  activebackground="#2a2a3a")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._text.configure(yscrollcommand=scrollbar.set)

        # Mensaje inicial
        self.log("info", "Escape Room Solver listo. Presiona ▶ Run para comenzar.")