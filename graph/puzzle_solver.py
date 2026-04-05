# puzzle_solver.py
# Punto 3 - Búsqueda informada (A*) para resolver acertijos de nodos bloqueados

import heapq
import time
from collections import deque


class PuzzleSolver:
    """
    Resuelve el acertijo de un nodo bloqueado usando A*.

    Recibe el dict 'puzzle' que ya viene definido en example_graph.py:
        {
            "nodes": [...],
            "edges": [(desde, hasta, costo), ...],
            "start": "S",
            "goal":  "E"
        }
    """

    def __init__(self, puzzle: dict):
        self.start = puzzle["start"]
        self.goal  = puzzle["goal"]

        # Grafo del puzzle como lista de adyacencia
        self.adj = {n: [] for n in puzzle["nodes"]}
        for (u, v, cost) in puzzle["edges"]:
            self.adj[u].append((v, cost))

        # Heurística admisible calculada automáticamente
        self.h = self._compute_heuristic(puzzle)

        # Métricas
        self.nodes_expanded = 0
        self.total_cost     = 0
        self.execution_time = 0.0
        self.path           = []
        self.log            = []  

    # ── HEURÍSTICA ────────────────────────────────────────────────────
    # h(n) = saltos_mínimos_al_goal × costo_mínimo_de_arista
    # Siempre admisible: nunca sobreestima el costo real.
    def _compute_heuristic(self, puzzle: dict) -> dict:
        all_costs = [c for (_, _, c) in puzzle["edges"]]
        min_cost  = min(all_costs) if all_costs else 1

        # Grafo invertido para BFS desde el goal hacia atrás
        reverse = {n: [] for n in puzzle["nodes"]}
        for (u, v, _) in puzzle["edges"]:
            reverse[v].append(u)

        # BFS para contar saltos mínimos de cada nodo al goal
        hops  = {n: float("inf") for n in puzzle["nodes"]}
        hops[self.goal] = 0
        queue = deque([self.goal])

        while queue:
            node = queue.popleft()
            for prev in reverse[node]:
                if hops[prev] == float("inf"):
                    hops[prev] = hops[node] + 1
                    queue.append(prev)

        return {n: hops[n] * min_cost for n in puzzle["nodes"]}

    # ── A* ────────────────────────────────────────────────────────────
    def solve(self) -> bool:
        start_time = time.time()

        # heap: (f, g, nodo_actual, camino)
        heap = []
        heapq.heappush(heap, (self.h[self.start], 0, self.start, [self.start]))

        visited = set()

        while heap:
            f, g, current, path = heapq.heappop(heap)

            if current in visited:
                continue
            visited.add(current)

            self.nodes_expanded += 1
            self.log.append(f"> Expanding node {{{current}}}")

            # ¿Llegamos al goal?
            if current == self.goal:
                self.path           = path
                self.total_cost     = g
                self.execution_time = round(time.time() - start_time, 4)
                self.log.append("- Puzzle Solved! Unlocking Node")
                return True

            # Expandir vecinos
            for (neighbor, cost) in self.adj[current]:
                if neighbor not in visited:
                    new_g = g + cost
                    new_f = new_g + self.h.get(neighbor, 0)
                    heapq.heappush(heap, (new_f, new_g, neighbor, path + [neighbor]))

        self.execution_time = round(time.time() - start_time, 4)
        self.log.append("- No solution found for puzzle.")
        return False

    # ── MÉTRICAS ──────────────────────────────────────────────────────
    def get_metrics(self) -> dict:
        return {
            "nodes_expanded": self.nodes_expanded,
            "total_cost":     self.total_cost,
            "execution_time": self.execution_time,
            "path":           self.path,
        }

    def print_metrics(self):
        print("\n── Local Puzzle Metrics ──────────────────")
        print(f"  Nodes Expanded : {self.nodes_expanded}")
        print(f"  Total Cost     : {self.total_cost}")
        print(f"  Execution Time : {self.execution_time}s")
        print(f"  Path Found     : {' → '.join(self.path)}")
        print("──────────────────────────────────────────")

    def print_log(self):
        print("\n── Puzzle Solver Log ─────────────────────")
        for line in self.log:
            print(f"  {line}")
        print("──────────────────────────────────────────")


if __name__ == "__main__":
    puzzle_C = {
        "nodes": ["S", "B", "C", "D", "E"],
        "edges": [
            ("S", "B", 7),
            ("B", "C", 8),
            ("B", "D", 3),
            ("D", "E", 2),
            ("C", "E", 4),
        ],
        "start": "S",
        "goal":  "E"
    }

    solver = PuzzleSolver(puzzle_C)
    solved = solver.solve()

    solver.print_log()
    solver.print_metrics()