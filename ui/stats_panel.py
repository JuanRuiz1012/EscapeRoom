import tkinter as tk


BG      = "#0a0a12"
SURFACE = "#0f0f1a"
BORDER  = "#1a1a2e"
TEXT    = "#e2e8f0"
MUTED   = "#64748b"
HINT    = "#2a2a4a"

ACCENT_BLUE   = "#3b82f6"
ACCENT_GREEN  = "#22c55e"
ACCENT_AMBER  = "#f59e0b"
ACCENT_PURPLE = "#a855f7"


class StatsPanel(tk.Frame):
    """
    Panel de estadísticas dividido en dos secciones:
        - Global Search  (búsqueda no informada)
        - Local Puzzle   (A*)

    API:
        panel.update_global(nodes_expanded, depth)
        panel.update_puzzle(nodes_expanded, total_cost)
        panel.set_time(seconds_float)
        panel.reset()
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._build()

    # API pública

    def update_global(self, nodes_expanded: int, depth: int):
        self._g_nodes.set(str(nodes_expanded))
        self._g_depth.set(str(depth))

    def update_puzzle(self, nodes_expanded: int, total_cost: int | float):
        self._p_nodes.set(str(nodes_expanded))
        self._p_cost.set(str(total_cost))

    def set_time(self, seconds: float):
        self._time.set(f"{seconds:.3f}s")

    def reset(self):
        for var in (self._g_nodes, self._g_depth,
                    self._p_nodes, self._p_cost):
            var.set("0")
        self._time.set("0.000s")

    # Construcción

    def _build(self):
        self.columnconfigure(0, weight=1)

        # ── Título ──
        title = tk.Label(self, text="ESTADÍSTICAS", bg=BG,
                         fg=MUTED, font=("Courier", 9, "bold"),
                         anchor="w", pady=6, padx=10)
        title.grid(row=0, column=0, sticky="ew")

        self._separator(row=1)

        # ── Global Search ──
        self._section_label("Global Search", ACCENT_BLUE, row=2)

        row_g = tk.Frame(self, bg=BG)
        row_g.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 8))
        row_g.columnconfigure((0, 1), weight=1)

        self._g_nodes = tk.StringVar(value="0")
        self._g_depth = tk.StringVar(value="0")
        self._metric_card(row_g, col=0, label="nodos expandidos",
                          var=self._g_nodes, accent=ACCENT_BLUE)
        self._metric_card(row_g, col=1, label="profundidad",
                          var=self._g_depth, accent=TEXT)

        self._separator(row=4)

        # ── Local Puzzle ──
        self._section_label("Local Puzzle  (A*)", ACCENT_AMBER, row=5)

        row_p = tk.Frame(self, bg=BG)
        row_p.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 8))
        row_p.columnconfigure((0, 1), weight=1)

        self._p_nodes = tk.StringVar(value="0")
        self._p_cost  = tk.StringVar(value="0")
        self._metric_card(row_p, col=0, label="nodos expandidos",
                          var=self._p_nodes, accent=ACCENT_AMBER)
        self._metric_card(row_p, col=1, label="costo total",
                          var=self._p_cost,  accent=ACCENT_GREEN)

        self._separator(row=7)

        # ── Tiempo ──
        time_frame = tk.Frame(self, bg=SURFACE, padx=10, pady=8)
        time_frame.grid(row=8, column=0, sticky="ew", padx=10, pady=(4, 10))
        time_frame.columnconfigure(0, weight=1)

        tk.Label(time_frame, text="tiempo de ejecución", bg=SURFACE,
                 fg=HINT, font=("Courier", 8)).grid(row=0, column=0, sticky="w")

        self._time = tk.StringVar(value="0.000s")
        tk.Label(time_frame, textvariable=self._time, bg=SURFACE,
                 fg=ACCENT_PURPLE, font=("Courier", 16, "bold")).grid(
                 row=1, column=0, sticky="w")

    def _section_label(self, text, color, row):
        f = tk.Frame(self, bg=BG)
        f.grid(row=row, column=0, sticky="ew", padx=10, pady=(6, 4))
        f.columnconfigure(1, weight=1)
        tk.Label(f, text="▸", bg=BG, fg=color,
                 font=("Courier", 9, "bold")).grid(row=0, column=0, padx=(0, 4))
        tk.Label(f, text=text, bg=BG, fg=color,
                 font=("Courier", 9, "bold"), anchor="w").grid(row=0, column=1, sticky="w")
        tk.Frame(f, bg=BORDER, height=1).grid(row=0, column=2, sticky="ew", padx=(6, 0))
        f.columnconfigure(2, weight=1)

    def _metric_card(self, parent, col, label, var, accent):
        card = tk.Frame(parent, bg=SURFACE, padx=10, pady=8)
        card.grid(row=0, column=col, sticky="nsew",
                  padx=(0 if col else 0, 6 if col == 0 else 0))

        tk.Label(card, text=label, bg=SURFACE, fg=HINT,
                 font=("Courier", 8)).pack(anchor="w")
        tk.Label(card, textvariable=var, bg=SURFACE,
                 fg=accent, font=("Courier", 22, "bold")).pack(anchor="w")

    def _separator(self, row):
        tk.Frame(self, bg=BORDER, height=1).grid(
            row=row, column=0, sticky="ew", padx=10, pady=2)