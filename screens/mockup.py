import asyncio

from startupbuddykernel import bootstrap
from startupbuddykernel.kernel import Kernel, SysCommand

from textual.app import ComposeResult
from textual.containers import VerticalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static, Link, Markdown
from textual import on, work, log
from interfaces.fs import ProjectDirClass
import interfaces
import os

class MockupScreen(Screen):
    """Generates a website mockup for the current business and displays the result."""

    CSS = """
    #mscreen {
        width: 55;
        align: center middle;
        padding-left: 2;
    }

    #mockup-status {
        width: 100%;
        text-style: bold;
    }

    #mockup-results {
        width: 100%;
        height: auto;
        max-height: 24;
        overflow-y: auto;
    }

    #mockup-results Static {
        margin-bottom: 1;
    }

    #regenerate {
        display: none;
        margin: 1;
    }

    #instructions {
       width: 45;
       border-right: solid white;
       height: 1fr;
    }

    #go-to-menu {
        display: none;
        margin: 1;
    }
    """

    kernel = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Markdown(id="instructions")
            with Vertical(id="mscreen"):
                yield Static("Creating your website mockup now...", id="mockup-status")
                yield VerticalScroll(id="mockup-results")
                yield Button("Generate another mockup", id="regenerate")
                yield Button("Go to main menu", id="go-to-menu")
            
        yield Footer()

    def on_mount(self) -> None:
        self.kernel = bootstrap()
        self.project = self.app.db.get_project(self.app.CURRENT_KERNEL_ID)
        bl = os.path.dirname(__file__)
        fp = open(os.path.join(bl, "./texts/mockup_instructions.md"))
        content = fp.read()
        markdown = self.query_one("#instructions", Markdown)
        markdown.update(content)
        dl = ProjectDirClass(self.project['folder'])
        contents = dl.read_file("pitches/pitch.md")
        log(f" the contents are {contents}")
        sections = interfaces.parse_sections(contents)
        log(f"the sections are {sections}")
        self.mockup_prompt = ""
        for key in sections.keys():
            if 'Two Minute' in key or '2-Minute' in key:
                self.mockup_prompt = sections[key]
        self.create_mockup()

    @work(exclusive=True)
    async def create_mockup(self) -> None:
        status = self.query_one("#mockup-status", Static)
        results = self.query_one("#mockup-results", VerticalScroll)
        button = self.query_one("#regenerate", Button)
        menu_button = self.query_one("#go-to-menu", Button)

        # reset the UI for a fresh run (also handles the "generate another" case)
        status.display = True
        button.display = False
        menu_button.display = False
        results.remove_children()

        # answers = getattr(self.app, "business_answers", []) or []
        # prompt = " ".join(a for a in answers if a) or "A modern landing page for a new startup."
        

        try:
            result = await asyncio.to_thread(
                self.kernel.cmd, SysCommand.CREATE_MOCKUP, prompt=self.mockup_prompt
            )
        except Exception as error:  # kernel / model failure — show it instead of crashing
            results.mount(Static(f"Sorry, I couldn't create the mockup: {error}"))
        else:
            if result.code == Kernel.ExitCode.GOOD:
                results.mount(Static(f"Your website mockup is ready:\n\n"))
                results.mount(Link(f"{result.data['url']}"))
            else:
                results.mount(Static(result.data.get("msg", "Something went wrong creating your mockup.")))

        # the command returned — hide the status and offer another run
        status.display = False
        button.display = True
        menu_button.display = True

    @on(Button.Pressed, "#regenerate")
    def regenerate(self, event: Button.Pressed) -> None:
        self.create_mockup()

    @on(Button.Pressed, "#go-to-menu")
    def go_to_menu(self, event: Button.Pressed) -> None:
        self.dismiss()
