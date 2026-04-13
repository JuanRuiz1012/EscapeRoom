import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.example_graph import build_example_graph
from ui.main_window import MainWindow
from search import run_search


def main():
    escape_graph = build_example_graph()
    app = MainWindow(escape_graph)

    # conecta el solver al boton Run de la interfaz
    app.on_run = run_search

    app.run()


if __name__ == "__main__":
    main()