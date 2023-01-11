"""
Code browser example.

Run with:

    python csv_plotter.py PATH

"""
import sys

import pandas as pd
import plotext as plt
from rich.traceback import Traceback
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import var
from textual.widgets import Button, DataTable, DirectoryTree, Footer, Header, Input, Static
from textual_autocomplete import AutoComplete, Dropdown, DropdownItem


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
        self.sub_title = csv_file

        data_table: DataTable = self.query_one("DataTable")
        data_table.clear(columns=True)

        try:
            self.df = pd.read_csv(csv_file)
        except Exception:
            self.df = pd.DataFrame()

        data_table.add_columns(*self.df.columns)
        for row in self.df.itertuples(index=False):
            data_table.add_row(*[str(x) for x in row])

        for i in ["#input-x", "#input-y"]:
            input_widget: Input = self.query_one(i)
            input_widget.value = ""
            input_dropdown: Dropdown = self.query_one(f"{i}-dropdown")
            input_dropdown.items = [DropdownItem(col.label.plain) for col in data_table.columns]

        plot_region: Static = self.query_one("#plot-region")
        plot_region.update("")

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        path = "./" if len(sys.argv) < 2 else sys.argv[1]
        yield Header()
        yield Container(
            DirectoryTree(path, id="tree-view"),
            DataTable(),
            id="data-container"
        )
        yield Container(
            Container(
                AutoComplete(
                    Input(placeholder="X axis", id="input-x"),
                    Dropdown(items=[], id="input-x-dropdown")
                ),
                AutoComplete(
                    Input(placeholder="Y axis", id="input-y"),
                    Dropdown(items=[], id="input-y-dropdown")
                ),
                Button("Plot!", id="button-plot", variant="primary"),
                id="plot-settings",
            ),
            Static(id="plot-region"),
            id="plot-container"
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        plot_region: Static = self.query_one("#plot-region")
        plot_region.update("")
        
        try:
            if button_id == "button-plot":
                input_x = self.query_one("#input-x").value
                input_y = self.query_one("#input-y").value

                plt.plot_size(50, 20)
                plt.scatter(
                    self.df[input_x],
                    self.df[input_y]
                )
                plt.xlabel(input_x)
                plt.ylabel(input_y)
                plot_str = plt.build()
                plot_region.update(f"{input_x=} {input_y=}\n{plot_str}")
        except Exception:
            plot_region.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree


if __name__ == "__main__":
    CsvPlotter().run()
