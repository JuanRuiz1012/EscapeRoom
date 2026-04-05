import tkinter as tk
import math


BG         = "#0a0a12"
GRID_COLOR = "#0e0e1c"

COLOR = {
    "start":    {"fill": "#22c55e", "outline": "#16a34a", "text": "#ffffff"},
    "goal":     {"fill": "#ef4444", "outline": "#dc2626", "text": "#ffffff"},
    "explored": {"fill": "#3b82f6", "outline": "#2563eb", "text": "#ffffff"},
    "active":   {"fill": "#0f0f1a", "outline": "#f59e0b", "text": "#f59e0b"},
    "idle":     {"fill": "#13131f", "outline": "#2a2a3a", "text": "#4a4a6a"},
}

NODE_RADIUS = 22


class PuzzleCanvas(tk.Canvas):
    """
    Canvas que muestra el subgrafo del puzzle (búsqueda informada A*).

    API:
        canvas.load_puzzle(puzzle_dict)     # carga el puzzle desde el nodo bloqueado
        canvas.set_explored(node_id)        # marca un nodo como explorado
        canvas.set_active(node_id)          # resalta nodo en expansión actual
        canvas.mark_solved()                # resalta el nodo goal como resuelto
        canvas.reset()                      # limpia todo
        canvas.refresh()                    # redibuja
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, highlightthickness=0, **kwargs)
        self.puzzle        = None      # dict con nodes, edges, start, goal
        self.node_states   = {}        # node_id → "idle"|"explored"|"active"|"start"|"goal"
        self.node_pos_norm = {}        # node_id → (nx, ny) en 0..1
        self.active_node   = None
        self.solved        = False

        self.bind("<Configure>", lambda e: self.refresh())

    # ── API pública ──────────────────────────────────────────────────────────

    def load_puzzle(self, puzzle_dict):
        """
        puzzle_dict tiene la forma:
            {
                "nodes": [...],
                "edges": [(from, to, cost), ...],
                "start": "...",
                "goal":  "..."
            }
        """
        self.puzzle      = puzzle_dict
        self.solved      = False
        self.active_node = None
        self.node_states = {}

        nodes = puzzle_dict["nodes"]
        self._auto_layout(nodes, puzzle_dict["start"], puzzle_dict["goal"])

        for n in nodes:
            if n == puzzle_dict["start"]:
                self.node_states[n] = "start"
            elif n == puzzle_dict["goal"]:
                self.node_states[n] = "goal"
            else:
                self.node_states[n] = "idle"

        self.refresh()

    def set_explored(self, node_id):
        if node_id in self.node_states and self.node_states[node_id] not in ("start", "goal"):
            self.node_states[node_id] = "explored"
        self.refresh()

    def set_active(self, node_id):
        self.active_node = node_id
        self.refresh()

    def mark_solved(self):
        self.solved = True
        self.active_node = None
        self.refresh()

    def reset(self):
        self.puzzle      = None
        self.node_states = {}
        self.active_node = None
        self.solved      = False
        self.refresh()

    def refresh(self):
        self.delete("all")
        if not self.puzzle:
            self._draw_idle()
            return
        self._draw_grid()
        self._draw_edges()
        self._draw_nodes()
        if self.solved:
            self._draw_solved_banner()

    # ── Layout automático ────────────────────────────────────────────────────

    def _auto_layout(self, nodes, start, goal):
        """Distribuye los nodos: start a la izquierda, goal a la derecha, resto en medio."""
        middle = [n for n in nodes if n != start and n != goal]
        self.node_pos_norm = {}
        self.node_pos_norm[start] = (0.10, 0.50)
        self.node_pos_norm[goal]  = (0.90, 0.50)

        count = len(middle)
        if count == 0:
            return
        for i, n in enumerate(middle):
            col = 0.35 + (i % 2) * 0.25
            row = 0.30 + (i // 2) * 0.40
            self.node_pos_norm[n] = (col, min(row, 0.85))

    def _px(self, node_id):
        w = max(self.winfo_width(),  10)
        h = max(self.winfo_height(), 10)
        nx_, ny_ = self.node_pos_norm.get(node_id, (0.5, 0.5))
        return nx_ * w, ny_ * h

    # ── Dibujo ───────────────────────────────────────────────────────────────

    def _draw_idle(self):
        w, h = self.winfo_width(), self.winfo_height()
        self.create_text(w // 2, h // 2,
                         text="— puzzle solver idle —",
                         fill="#2a2a3a", font=("Courier", 11))

    def _draw_grid(self):
        w, h = self.winfo_width(), self.winfo_height()
        for x in range(0, w, 40):
            self.create_line(x, 0, x, h, fill=GRID_COLOR, width=1)
        for y in range(0, h, 40):
            self.create_line(0, y, w, y, fill=GRID_COLOR, width=1)

    def _draw_edges(self):
        for u, v, cost in self.puzzle["edges"]:
            x1, y1 = self._px(u)
            x2, y2 = self._px(v)
            self._arrow(x1, y1, x2, y2, "#2a2a3a", NODE_RADIUS)
            mx = (x1 + x2) / 2 + 10
            my = (y1 + y2) / 2 - 10
            self.create_text(mx, my, text=str(cost),
                             fill="#4a4a7a", font=("Courier", 10, "bold"))

    def _draw_nodes(self):
        r = NODE_RADIUS
        for node in self.puzzle["nodes"]:
            px, py = self._px(node)
            is_active = (node == self.active_node)
            state = "active" if is_active else self.node_states.get(node, "idle")
            c = COLOR.get(state, COLOR["idle"])

            if is_active:
                self.create_oval(px - r - 8, py - r - 8,
                                 px + r + 8, py + r + 8,
                                 fill="", outline="#f59e0b", width=1)

            self.create_oval(px - r, py - r, px + r, py + r,
                             fill=c["fill"], outline=c["outline"],
                             width=2 if is_active else 1)

            self.create_text(px, py, text=node,
                             fill=c["text"], font=("Courier", 11, "bold"))

    def _draw_solved_banner(self):
        w, h = self.winfo_width(), self.winfo_height()
        self.create_rectangle(0, h - 28, w, h, fill="#052e16", outline="")
        self.create_text(w // 2, h - 14,
                         text="✓  Puzzle Solved! Nodo desbloqueado.",
                         fill="#22c55e", font=("Courier", 10, "bold"))

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