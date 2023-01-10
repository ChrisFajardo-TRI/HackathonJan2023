"""
Code browser example.

Run with:

    python csv_plotter.py PATH

"""
import sys

import pandas as pd
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import var
from textual.widgets import DataTable, DirectoryTree, Footer, Header


class CsvPlotter(App):
    """Textual csv plotter app."""

    CSS_PATH = "csv_plotter.css"
    BINDINGS = [
        ("f", "toggle_files", "Toggle Files"),
        ("q", "quit", "Quit"),
    ]

    show_tree = var(True)
    csv_file = var("")

    df = pd.DataFrame()

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def watch_csv_file(self, csv_file: str) -> None:
        data_table: DataTable = self.query_one("DataTable")
        data_table.clear(columns=True)

        try:
            self.df = pd.read_csv(csv_file)
        except Exception:
            self.df = pd.DataFrame()

        data_table.add_columns(*self.df.columns)
        for row in self.df.itertuples(index=False):
            data_table.add_row(*[str(x) for x in row])

    def watch_loading(self, loading: bool):
        self.query_one("#progress-bar").set_class(loading, "-show-loading")

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        path = "./" if len(sys.argv) < 2 else sys.argv[1]
        yield Header()
        yield Container(
            DirectoryTree(path, id="tree-view"),
            DataTable()
        )
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        self.csv_file = event.path

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree


if __name__ == "__main__":
    CsvPlotter().run()
