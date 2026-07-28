from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Label, ListItem, ListView, Static, Markdown
from textual import on
import os


class MenuScreen(Screen):
    CSS = """
    #project-header {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1 0;
    }
    #project-name {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: black;
        background: $accent;
        padding: 1 0;
    }
    #project-directory {
        width: 100%;
        text-align: center;
        text-style: dim;
    }

    #menu {
      padding: 1;
    }
    #instructions {
      width: 40%;
    }
    """

    # (label shown in the list, screen name to open when selected)
    MENU_ITEMS = [
        ("Business Idea", "questions"),
        ("Create Your Pitch", "pitch"),
        ("Website Mockup", "mockup"),
        # ("Kernel Development", "chat"),
        ("Select Different Project", "main")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("", id="project-name"),
            Static("", id="project-directory"),
            id="project-header",
        )
        with Horizontal():
            yield Markdown(id="instructions")
            with Vertical():
                yield ListView(id="menu",
                    *(ListItem(Label(label), id=screen) for label, screen in self.MENU_ITEMS)
                )
        yield Footer()

    async def on_mount(self) -> None:
        bl = os.path.dirname(__file__)
        md = self.query_one("#instructions", Markdown)
        await md.load(os.path.join(bl, "./texts/app_instructions.md"))
        self._refresh_project()

    def on_screen_resume(self) -> None:
        # MenuScreen is a cached singleton in StartupBuddy.SCREENS, so re-read the
        # current project each time the screen is shown (it may have changed).
        self._refresh_project()

    def _refresh_project(self) -> None:
        project = self.app.db.get_project(self.app.CURRENT_KERNEL_ID)
        if project:
            name = " ".join(project["name"].upper())
            directory = project.get("folder") or ""
        else:
            name = "NO PROJECT SELECTED"
            directory = ""
        if project and "business_answers" in project:
            self.app.business_answers = project['business_answers']
        self.query_one("#project-name", Static).update(name)
        self.query_one("#project-directory", Static).update(directory)

    @on(ListView.Selected)
    def open_selected(self, event: ListView.Selected) -> None:
        if event.item.id == "questions":
            self.app.push_screen(event.item.id, self.app.business_questions_answered)
        elif event.item.id == "pitch":
            self.app.push_screen(event.item.id, self.app.pitch_created)
        elif event.item.id == "mockup":
            self.app.push_screen(event.item.id, self.app.pitch_created)
        elif event.item.id == "chat":
            self.app.push_screen(event.item.id, self.app.pitch_created)
        elif event.item.id == "main":
            # "Select Different Project": reuse the startup selection handler so
            # CURRENT_KERNEL_ID is updated with the newly chosen project.
            self.app.push_screen(event.item.id, self.app.check_main_selection)
        else:
            self.app.business_answers = None
            self.app.push_screen(event.item.id)
