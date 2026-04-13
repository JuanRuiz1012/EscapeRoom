import tkinter as tk
import math


# Colores por estado
COLOR = {
    "solved":    {"fill": "#22c55e", "outline": "#16a34a", "text": "#ffffff"},
    "available": {"fill": "#3b82f6", "outline": "#2563eb", "text": "#ffffff"},
    "locked":    {"fill": "#1e1e2e", "outline": "#6b7280", "text": "#6b7280"},
    "expanding": {"fill": "#0f0f1a", "outline": "#f59e0b", "text": "#f59e0b"},
    "goal":      {"fill": "#a855f7", "outline": "#9333ea", "text": "#ffffff"},
}

NODE_RADIUS = 22
EDGE_COLOR  = "#2a2a3a"
EDGE_HOVER  = "#f59e0b"
BG          = "#0a0a12"
GRID_COLOR  = "#111122"

# Posiciones fijas normalizadas (0..1) para el grafo del ejemplo
DEFAULT_POSITIONS = {
    "A": (0.10, 0.48),
    "B": (0.30, 0.20),
    "E": (0.30, 0.72),
    "C": (0.52, 0.20),
    "G": (0.52, 0.55),
    "H": (0.30, 0.92),
    "I": (0.68, 0.28),
    "K": (0.68, 0.65),
    "J": (0.52, 0.88),
    "L": (0.87, 0.20),
    "M": (0.87, 0.65),
}


class GraphCanvas(tk.Canvas):
    """
    Canvas que dibuja el grafo global del Escape Room.

    Uso desde el exterior:
        canvas.set_graph(escape_graph)          # carga el grafo
        canvas.set_expanding(node_id)           # resalta nodo que se expande
        canvas.refresh()                        # redibuja
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, highlightthickness=0, **kwargs)
        self.escape_graph   = None
        self.expanding_node = None
        self.node_positions = {}   # node_id → (x_px, y_px)
        self.on_node_click  = None # callback(node_id)

        self.bind("<Configure>", lambda e: self.refresh())
        self.bind("<Button-1>",  self._on_click)

    # API pública

    def set_graph(self, escape_graph, positions: dict = None):
        """Carga un EscapeGraph. positions = {node_id: (nx, ny)} en 0..1."""
        self.escape_graph = escape_graph
        self._positions_norm = positions or {}
        self.refresh()

    def set_expanding(self, node_id):
        self.expanding_node = node_id
        self.refresh()

    def clear_expanding(self):
        self.expanding_node = None
        self.refresh()

    def refresh(self):
        self.delete("all")
        if not self.escape_graph:
            self._draw_empty()
            return
        self._compute_positions()
        self._draw_grid()
        self._draw_edges()
        self._draw_nodes()

    # Dibujo interno

    def _draw_empty(self):
        w, h = self.winfo_width(), self.winfo_height()
        self.create_text(w // 2, h // 2, text="sin grafo cargado",
                         fill="#2a2a3a", font=("Courier", 11))

    def _draw_grid(self):
        w, h = self.winfo_width(), self.winfo_height()
        step = 40
        for x in range(0, w, step):
            self.create_line(x, 0, x, h, fill=GRID_COLOR, width=1)
        for y in range(0, h, step):
            self.create_line(0, y, w, y, fill=GRID_COLOR, width=1)

    def _compute_positions(self):
        w = max(self.winfo_width(),  10)
        h = max(self.winfo_height(), 10)
        self.node_positions = {}
        for node in self.escape_graph.get_all_nodes():
            nx_, ny_ = self._positions_norm.get(node, DEFAULT_POSITIONS.get(node, (0.5, 0.5)))
            self.node_positions[node] = (nx_ * w, ny_ * h)

    def _draw_edges(self):
        for u, v, data in self.escape_graph.get_all_edges():
            x1, y1 = self.node_positions.get(u, (0, 0))
            x2, y2 = self.node_positions.get(v, (0, 0))
            self._arrow(x1, y1, x2, y2, EDGE_COLOR, NODE_RADIUS)
            # costo si es > 1
            cost = data.get("cost", 1)
            if cost != 1:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                self.create_text(mx + 8, my - 8, text=str(cost),
                                 fill="#4a4a6a", font=("Courier", 9))

    def _draw_nodes(self):
        r = NODE_RADIUS
        for node in self.escape_graph.get_all_nodes():
            px, py = self.node_positions.get(node, (0, 0))
            expanding = (node == self.expanding_node)

            if expanding:
                state_key = "expanding"
            elif node == self.escape_graph.goal_node:
                state_key = "goal"
            else:
                state_key = self.escape_graph.get_status(node)

            c = COLOR.get(state_key, COLOR["available"])

            # Halo para el nodo en expansión
            if expanding:
                self.create_oval(px - r - 8, py - r - 8,
                                 px + r + 8, py + r + 8,
                                 fill="", outline="#f59e0b", width=1)

            # Círculo principal
            self.create_oval(px - r, py - r, px + r, py + r,
                             fill=c["fill"], outline=c["outline"],
                             width=2 if expanding else 1)

            # Borde punteado para nodos bloqueados
            if state_key == "locked":
                self._dashed_circle(px, py, r + 4, "#3a3a4a")

            # Etiqueta
            self.create_text(px, py, text=node,
                             fill=c["text"], font=("Courier", 11, "bold"))

            # Ícono de candado
            if state_key == "locked":
                self.create_text(px + r - 4, py - r + 4, text="🔒",
                                 font=("", 9))

    # Helpers de dibujo

    def _arrow(self, x1, y1, x2, y2, color, offset):
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return
        ux, uy = dx / length, dy / length
        sx, sy = x1 + ux * offset, y1 + uy * offset
        ex, ey = x2 - ux * offset, y2 - uy * offset
        self.create_line(sx, sy, ex, ey, fill=color, width=1,
                         arrow=tk.LAST, arrowshape=(8, 10, 4))

    def _dashed_circle(self, cx, cy, r, color, segments=24):
        step = 2 * math.pi / segments
        for i in range(0, segments, 2):
            a0 = i * step
            a1 = (i + 1) * step
            x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
            x1_, y1_ = cx + r * math.cos(a1), cy + r * math.sin(a1)
            self.create_line(x0, y0, x1_, y1_, fill=color, width=1)

    # Eventos

    def _on_click(self, event):
        if not self.on_node_click:
            return
        for node, (px, py) in self.node_positions.items():
            if math.hypot(event.x - px, event.y - py) <= NODE_RADIUS:
                self.on_node_click(node)
                return