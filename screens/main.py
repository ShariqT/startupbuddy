from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static, Header, Select, Button
from textual.containers import Horizontal
from textual import on, log
import os

def get_current_projects(db):
    projects = [('New Kernel', 1)]
    projects.extend((p['name'], p['id']) for p in db.get_projects())
    return projects

class MainScreen(Screen):
    CSS = """
    #api-key-banner {
        width: 100%;
        background: red;
        color: white;
        text-style: bold;
        text-align: center;
        padding-top: 2;
        padding-bottom: 2;
    }

    #clear-projects, #settings-panel {
        margin: 1;
    }

    Select {
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "You must set your Wavespeed API key before using",
            id="api-key-banner",
        )
        # yield Static("StartupBuddy -- the tool that helps you jumpstart your idea!")
        yield Static("Select an existing project from the dropdown menu")
        yield Select((name, (name, project_id)) for name, project_id in get_current_projects(self.app.db))
        
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
        if missing is False:
            os.environ['WAVESPEED_API_KEY'] = settings['api_key']

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        if event.value is Select.BLANK:
            return
        self.dismiss(event.value)

    # @on(Button.Pressed, "#settings-panel")
    # def open_settings(self, event: Button.Pressed) -> None:
    #     self.app.push_screen("settings")

    # @on(Button.Pressed, "#clear-projects")
    # def clear_projects(self, event: Button.Pressed) -> None:
    #     self.app.db.clear_projects()
    #     self.app.CURRENT_KERNEL_ID = None
    #     self.query_one(Select).set_options(
    #         (name, (name, project_id))
    #         for name, project_id in get_current_projects(self.app.db)
    #     )
  

   