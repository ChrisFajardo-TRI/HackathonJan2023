from textual.app import App, ComposeResult

from textual.widgets import Static
import plotext as plt


class PlotextApp(App):
    BINDINGS = [("q", "request_quit", "Quit")]

    def compose(self) -> ComposeResult:
        plt.scatter(plt.sin())

        yield Static(plt.build())

    def action_request_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = PlotextApp()
    app.run()
