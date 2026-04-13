import tkinter as tk
import time
import threading

from ui.graph_canvas  import GraphCanvas
from ui.puzzle_canvas import PuzzleCanvas
from ui.stats_panel   import StatsPanel
from ui.console_panel import ConsolePanel


BG      = "#0a0a12"
SURFACE = "#0f0f1a"
BORDER  = "#1a1a2e"
TEXT    = "#e2e8f0"
MUTED   = "#4a4a6a"
ACCENT  = "#3b82f6"

ALGO_LABELS = {"bfs": "BFS", "dfs": "DFS"}


class MainWindow:

    def __init__(self, escape_graph=None):
        self.escape_graph = escape_graph
        self.algo         = "bfs"
        self._running     = False
        self._start_time  = None
        self._timer_id    = None

        # Callbacks que el backend puede sobreescribir
        self.on_run   = None   # fn(escape_graph, algo, app)
        self.on_step  = None   # fn(escape_graph, algo, app)
        self.on_reset = None   # fn(app)

        self._build_window()
        self._build_ui()

        if escape_graph:
            self.load_graph(escape_graph)

    # Ventana

    def _build_window(self):
        self.root = tk.Tk()
        self.root.title("Escape Room Solver")
        self.root.configure(bg=BG)
        self.root.geometry("1200x720")
        self.root.minsize(1200, 900)

        # Icono (opcional, falla silencioso si no existe)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except Exception:
            pass

    # UI

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()
        self._build_bottom()

    def _build_header(self):
        header = tk.Frame(self.root, bg=SURFACE, pady=0)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        # Dots decorativos
        dots = tk.Frame(header, bg=SURFACE, padx=14, pady=10)
        dots.grid(row=0, column=0)
        for color in ("#ef4444", "#f59e0b", "#22c55e"):
            tk.Label(dots, text="●", bg=SURFACE, fg=color,
                     font=("", 10)).pack(side="left", padx=2)

        # Título
        tk.Label(header, text="Escape Room Solver",
                 bg=SURFACE, fg=TEXT,
                 font=("Courier", 13, "bold")).grid(row=0, column=1, sticky="w")

        # Controles derecha
        ctrl = tk.Frame(header, bg=SURFACE, padx=14)
        ctrl.grid(row=0, column=2)

        # Selector de algoritmo
        self._algo_var = tk.StringVar(value="bfs")
        algo_menu = tk.OptionMenu(ctrl, self._algo_var, "bfs", "dfs",
                                   command=self._on_algo_change)
        algo_menu.configure(bg=SURFACE, fg=MUTED, activebackground=SURFACE,
                             activeforeground=TEXT, highlightthickness=0,
                             font=("Courier", 9), bd=0, relief="flat")
        algo_menu["menu"].configure(bg=SURFACE, fg=TEXT,
                                     activebackground="#1a1a3a",
                                     font=("Courier", 9))
        algo_menu.pack(side="left", padx=(0, 8))

        # Botones
        for label, cmd, style in [
            ("▶  Run",  self._on_run,   "primary"),
            ("⏭  Step", self._on_step,  "normal"),
            ("↺  Reset",self._on_reset, "normal"),
        ]:
            self._make_btn(ctrl, label, cmd, style)

        # Badge de estado
        self._status_var = tk.StringVar(value="ready")
        tk.Label(ctrl, textvariable=self._status_var,
                 bg=SURFACE, fg=MUTED,
                 font=("Courier", 9), padx=10).pack(side="left")

        tk.Frame(header, bg=BORDER, height=1).grid(
            row=1, column=0, columnspan=3, sticky="ew")

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=3)
        body.columnconfigure(2, weight=2)

        # ── Grafo Global ──
        left = tk.Frame(body, bg=SURFACE)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
        self._panel_header(left, "Global Graph", "Búsqueda no informada", row=0)
        self.global_canvas = GraphCanvas(left)
        self.global_canvas.grid(row=1, column=0, sticky="nsew")
        self._legend_bar(left, [
            ("solved",    "#22c55e", "resuelto"),
            ("available", "#3b82f6", "disponible"),
            ("locked",    "#6b7280", "bloqueado"),
            ("expand",    "#f59e0b", "expandiendo"),
        ], row=2)

        # ── Puzzle Solver ──
        mid = tk.Frame(body, bg=SURFACE)
        mid.grid(row=0, column=1, sticky="nsew", padx=4)
        mid.rowconfigure(1, weight=1)
        mid.columnconfigure(0, weight=1)
        self._panel_header(mid, "Puzzle Solver", "Búsqueda informada (A*)", row=0)
        self.puzzle_canvas = PuzzleCanvas(mid)
        self.puzzle_canvas.grid(row=1, column=0, sticky="nsew")
        self._legend_bar(mid, [
            ("start",    "#22c55e", "inicio"),
            ("goal",     "#ef4444", "meta"),
            ("explored", "#3b82f6", "explorado"),
            ("active",   "#f59e0b", "activo"),
        ], row=2)

        # ── Stats ──
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=2, sticky="nsew", padx=(4, 0))
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)
        self.stats = StatsPanel(right)
        self.stats.grid(row=0, column=0, sticky="nsew")

    def _build_bottom(self):
        bottom = tk.Frame(self.root, bg=BG)
        bottom.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        bottom.columnconfigure(0, weight=1)
        bottom.rowconfigure(0, weight=1)
        self.root.rowconfigure(2, minsize=180)

        self.console = ConsolePanel(bottom)
        self.console.grid(row=0, column=0, sticky="nsew",
                           ipady=0, ipadx=0)

    # Helpers de construcción

    def _panel_header(self, parent, title, subtitle, row=0):
        f = tk.Frame(parent, bg="#0c0c18", pady=6, padx=12)
        f.grid(row=row, column=0, sticky="ew")
        f.columnconfigure(0, weight=1)
        tk.Label(f, text=title, bg="#0c0c18", fg=TEXT,
                 font=("Courier", 11, "bold"), anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(f, text=subtitle, bg="#0c0c18", fg=MUTED,
                 font=("Courier", 8), anchor="w").grid(row=1, column=0, sticky="w")
        tk.Frame(parent, bg=BORDER, height=1).grid(row=row, column=0, sticky="sew")

    def _legend_bar(self, parent, items, row):
        bar = tk.Frame(parent, bg="#0c0c18", pady=5, padx=10)
        bar.grid(row=row, column=0, sticky="ew")
        tk.Frame(parent, bg=BORDER, height=1).grid(row=row, column=0, sticky="new")
        for _, color, label in items:
            dot = tk.Label(bar, text="●", bg="#0c0c18", fg=color, font=("", 8))
            dot.pack(side="left", padx=(0, 2))
            tk.Label(bar, text=label, bg="#0c0c18", fg=MUTED,
                     font=("Courier", 8)).pack(side="left", padx=(0, 10))

    def _make_btn(self, parent, text, cmd, style="normal"):
        if style == "primary":
            btn = tk.Button(parent, text=text, command=cmd,
                            bg=ACCENT, fg="#ffffff",
                            activebackground="#2563eb", activeforeground="#ffffff",
                            font=("Courier", 10, "bold"),
                            bd=0, padx=12, pady=4, cursor="hand2", relief="flat")
        else:
            btn = tk.Button(parent, text=text, command=cmd,
                            bg=SURFACE, fg=MUTED,
                            activebackground="#1a1a2e", activeforeground=TEXT,
                            font=("Courier", 10),
                            bd=0, padx=12, pady=4, cursor="hand2", relief="flat")
        btn.pack(side="left", padx=3)
        return btn

    # API pública para el backend

    def load_graph(self, escape_graph):
        """Carga y muestra un EscapeGraph en el canvas global."""
        self.escape_graph = escape_graph
        self.global_canvas.set_graph(escape_graph)

    def notify_expand(self, node_id: str, path: list = None):
        """Llamar cuando el algoritmo global expande un nodo."""
        self.global_canvas.set_expanding(node_id)
        self.console.log_expand(node_id, path)

    def notify_locked(self, node_id: str):
        """Llamar cuando se encuentra un nodo bloqueado."""
        self.global_canvas.set_expanding(node_id)
        self.console.log_locked(node_id)

    def notify_puzzle_start(self, puzzle_dict: dict):
        """Llamar cuando empieza la resolución del puzzle."""
        self.puzzle_canvas.load_puzzle(puzzle_dict)

    def notify_puzzle_step(self, node_id: str):
        """Llamar en cada expansión del A*."""
        self.puzzle_canvas.set_active(node_id)
        self.puzzle_canvas.set_explored(node_id)
        self.console.log_puzzle_step(node_id)

    def notify_puzzle_solved(self, goal_node: str, unlocked_node: str):
        """Llamar cuando el puzzle se resuelve."""
        self.puzzle_canvas.mark_solved()
        self.console.log_puzzle_solved(goal_node)
        self.console.log_unlock(unlocked_node)
        self.global_canvas.refresh()

    def notify_goal_reached(self, node_id: str):
        """Llamar cuando se alcanza la meta global."""
        self.global_canvas.clear_expanding()
        self.console.log_goal_reached(node_id)
        self._status_var.set("¡done!")
        self._stop_timer()

    def update_stats_global(self, nodes_expanded: int, depth: int):
        self.stats.update_global(nodes_expanded, depth)

    def update_stats_puzzle(self, nodes_expanded: int, total_cost):
        self.stats.update_puzzle(nodes_expanded, total_cost)

    # Botones

    def _on_algo_change(self, val):
        self.algo = val
        self.console.log_info(f"Algoritmo global cambiado a: {val.upper()}")

    def _on_run(self):
        if self._running:
            return
        self._running = True
        self._status_var.set("running…")
        self._start_time = time.time()
        self._tick_timer()

        if self.on_run:
            t = threading.Thread(
                target=self.on_run,
                args=(self.escape_graph, self.algo, self),
                daemon=True,
            )
            t.start()
        else:
            self.console.log_info("⚠  No hay solver conectado. Conecta on_run al backend.")

    def _on_step(self):
        if self.on_step:
            self.on_step(self.escape_graph, self.algo, self)
        else:
            self.console.log_info("⚠  No hay step handler conectado.")

    def _on_reset(self):
        self._running = False
        self._stop_timer()
        self._status_var.set("ready")
        self.puzzle_canvas.reset()
        self.stats.reset()
        self.console.clear()

        if self.escape_graph:
            # Reconstruye el grafo desde el ejemplo original
            from graph.example_graph import build_example_graph
            self.escape_graph = build_example_graph()
            self.global_canvas.set_graph(self.escape_graph)

        if self.on_reset:
            self.on_reset(self)

    # Timer

    def _tick_timer(self):
        if not self._running or not self._start_time:
            return
        elapsed = time.time() - self._start_time
        self.stats.set_time(elapsed)
        self._timer_id = self.root.after(100, self._tick_timer)

    def _stop_timer(self):
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
        self._running = False

    # Arranque

    def run(self):
        self.root.mainloop()