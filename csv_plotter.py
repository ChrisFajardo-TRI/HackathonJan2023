"""
Code browser example.

Run with:

    python csv_plotter.py PATH

"""
import os
import sys

import pandas as pd
from rich.traceback import Traceback
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
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

        for i in ["#input-x", "#input-y", "#input-color"]:
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
                AutoComplete(
                    Input(placeholder="Color by", id="input-color"),
                    Dropdown(items=[], id="input-color-dropdown")
                ),
                AutoComplete(
                    Input(placeholder="Plot type", id="input-plot-type"),
                    Dropdown(items=[
                        DropdownItem('scatter'),
                        DropdownItem('line'),
                        DropdownItem('bar')
                    ], id="input-plot-type-dropdown")
                ),
                Horizontal(
                    Button("plotly!", id="button-plotly", variant="default"),
                    Button("plotille!", id="button-plotille", variant="success"),
                    Button("plotext!", id="button-plotext", variant="primary"),
                    Button("clear!", id="button-clear", variant="error"),
                ),
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
        plot_width = 60
        plot_height = 35
        renderable = ""

        input_x = self.query_one("#input-x").value or None
        input_y = self.query_one("#input-y").value or None
        input_color = self.query_one("#input-color").value or None
        input_plot_type = self.query_one("#input-plot-type").value or "scatter"
        
        try:
            if button_id == "button-plotly":
                # plotly express (or same method for any plotting library than can save to file)
                import plotly.express as px
                from PIL import Image
                from rich_pixels import Pixels
                from tempfile import TemporaryDirectory
                input_plot_type_to_fn = {
                    'scatter': px.scatter,
                    'line': px.line,
                    'bar': px.scatter
                }
                fig = input_plot_type_to_fn[input_plot_type](self.df, x=input_x, y=input_y, color=input_color)
                with TemporaryDirectory() as td:
                    fig.write_image("plot.png", width=600, height=350)
                    renderable = Pixels.from_image_path("plot.png", resize=(plot_width, plot_height))

            elif button_id == "button-plotille":
                import plotille
                fig = plotille.Figure()
                input_plot_type_to_fn = {
                    'scatter': fig.scatter,
                    'line': fig.plot,
                    'bar': fig.scatter  # not supported
                }
                fig.clear()
                fig.width = plot_width
                fig.height = plot_height
                fig.color_mode = 'byte'
                if input_color:
                    for g, gdf in self.df.groupby(input_color):
                        input_plot_type_to_fn[input_plot_type](self.df[input_x], self.df[input_y], label=g)
                else:
                    input_plot_type_to_fn[input_plot_type](self.df[input_x], self.df[input_y])

                os.environ['FORCE_COLOR'] = '1'
                renderable = fig.show(legend=True)

            elif button_id == "button-plotext":
                import plotext as plt
                plt.clear_figure()
                input_plot_type_to_fn = {
                    'scatter': plt.scatter,
                    'line': plt.plot,
                    'bar': plt.bar
                }

                plt.plot_size(plot_width, plot_height)
                if input_color:
                    for i, (g, gdf) in enumerate(self.df.groupby(input_color)):
                        input_plot_type_to_fn[input_plot_type](self.df[input_x], self.df[input_y], label=g, color=i % 14)
                else:
                    input_plot_type_to_fn[input_plot_type](self.df[input_x], self.df[input_y])

                renderable = plt.build()

            plot_region.update(renderable)
        except Exception:
            plot_region.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree


if __name__ == "__main__":
    CsvPlotter().run()
