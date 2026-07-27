from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Static, RadioSet, RadioButton, Button
from textual import on, log
from textual.containers import Horizontal
import os

class StartScreen(Screen):
    CSS = """
    #api-key-banner {
        width: 100%;
        background: red;
        color: white;
        text-style: bold;
        text-align: center;
        padding: 1 0;
    }

    #welcome {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Welcome to StartupBuddy, the tool that will help you start your next big idea!",
            id="welcome",
        )
        yield Static(
            "You must set your Wavespeed API key before using",
            id="api-key-banner",
        )
        yield RadioSet(
            RadioButton("Start a new project", id="new-project"),
            RadioButton("Open an existing project", id="open-project"),
        )

        with Horizontal():
            yield Button("Settings Panel", id="settings-panel", variant="primary")
            yield Button("Clear All Projects", id="clear-projects", variant="error")

    def on_mount(self) -> None:
        self._refresh_api_key_banner()

    def on_screen_resume(self) -> None:
        # MainScreen is a cached singleton, so re-check the setting each time it shows.
        self._refresh_api_key_banner()

    def _refresh_api_key_banner(self) -> None:
        settings = self.app.db.get_settings()
        missing = not settings or "api_key" not in settings
        self.query_one("#api-key-banner", Static).display = missing
        log(f"The missing fvalue is {missing}")
        log(f"the settings is {settings}")
        if missing is False:
            os.environ['WAVESPEED_API_KEY'] = settings['api_key']
            log(f"the environment variable {os.environ['WAVESPEED_API_KEY']}")

    @on(RadioSet.Changed)
    def option_selected(self, event: RadioSet.Changed) -> None:
        if event.pressed.id == "new-project":
            self.app.push_screen("new_project", self.app.confirm_new_project_name)
        if event.pressed.id == "open-project":
            self.app.push_screen("main", self.app.check_main_selection)


    @on(Button.Pressed, "#settings-panel")
    def open_settings(self, event: Button.Pressed) -> None:
        self.app.push_screen("settings")

    @on(Button.Pressed, "#clear-projects")
    def clear_projects(self, event: Button.Pressed) -> None:
        self.app.db.clear_projects()
        self.app.CURRENT_KERNEL_ID = None
        self.query_one(Select).set_options(
            (name, (name, project_id))
            for name, project_id in get_current_projects(self.app.db)
        )
