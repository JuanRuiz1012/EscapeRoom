"""
main.py — Punto de entrada del Escape Room Solver
==================================================

Ejecuta:
    python main.py

Para conectar el solver del backend, implementa las funciones
`run_solver` y/o `step_solver` y asígnalas a app.on_run / app.on_step.

Ejemplo de integración con el backend:
---------------------------------------

    from solvers.bfs_solver import BFSSolver       # lo implementan sus compañeros
    from solvers.astar_solver import AStarSolver

    def run_solver(escape_graph, algo, app):
        solver = BFSSolver(escape_graph) if algo == "bfs" else DFSSolver(escape_graph)
        for event in solver.run():
            # event = {"type": "expand", "node": "B", "path": ["A","B"], ...}
            handle_event(event, app)

    def handle_event(event, app):
        t = event["type"]
        if t == "expand":
            app.notify_expand(event["node"], event.get("path"))
            app.update_stats_global(event["nodes_expanded"], event["depth"])
        elif t == "locked":
            app.notify_locked(event["node"])
        elif t == "puzzle_start":
            app.notify_puzzle_start(event["puzzle"])
        elif t == "puzzle_step":
            app.notify_puzzle_step(event["node"])
            app.update_stats_puzzle(event["nodes_expanded"], event["cost"])
        elif t == "puzzle_solved":
            app.notify_puzzle_solved(event["goal"], event["unlocked"])
        elif t == "goal":
            app.notify_goal_reached(event["node"])
        import time; time.sleep(0.6)   # pausa visual entre pasos

    app.on_run = run_solver
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from graph.example_graph import build_example_graph
from ui.main_window      import MainWindow


def main():
    escape_graph = build_example_graph()
    app = MainWindow(escape_graph)

    # ── Conecta aquí el solver del backend ──────────────────────────────────
    # app.on_run   = run_solver    # descomenta cuando el backend esté listo
    # app.on_step  = step_solver
    # app.on_reset = reset_solver
    # ────────────────────────────────────────────────────────────────────────

    app.run()


if __name__ == "__main__":
    main()