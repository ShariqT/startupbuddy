from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static
from textual import on


class SettingsScreen(Screen):
    """Application settings for the current kernel/project."""

    CSS = """
    SettingsScreen {
        align: center middle;
    }

    #settings-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding: 1;
    }

    #settings-body {
        width: 100%;
        height: auto;
        padding: 1 2;
    }

    #api-key-row {
        height: auto;
    }

    #api-key-input {
        width: 1fr;
    }

    #submit-api-key {
        margin-left: 1;
    }

    #settings-banner {
        width: 100%;
        background: green;
        color: white;
        text-style: bold;
        text-align: center;
        padding: 1 0;
        display: none;
    }

    #go-to-menu {
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Settings", id="settings-title")
        yield VerticalScroll(
            Label("Enter your Wavespeed API key"),
            Horizontal(
                Input(id="api-key-input"),
                Button("Submit", id="submit-api-key", variant="primary"),
                id="api-key-row",
            ),
            Static("Settings updated!", id="settings-banner"),
            id="settings-body",
        )
        yield Button("Go to main menu", id="go-to-menu")
        yield Footer()

    def on_mount(self) -> None:
        settings = self.app.db.get_settings()
        if settings and settings.get("api_key"):
            self.query_one("#api-key-input", Input).value = settings["api_key"]

    @on(Button.Pressed, "#submit-api-key")
    def save_api_key(self, event: Button.Pressed) -> None:
        api_key = self.query_one("#api-key-input", Input).value
        self.app.db.save_settings({"api_key": api_key})
        self.query_one("#settings-banner", Static).display = True

    @on(Button.Pressed, "#go-to-menu")
    def go_to_menu(self, event: Button.Pressed) -> None:
        self.dismiss()
