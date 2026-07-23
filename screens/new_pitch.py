import asyncio

from textual.screen import Screen
from startupbuddykernel import bootstrap
from startupbuddykernel.kernel import Kernel, SysCommand
from datetime import datetime
import os
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Footer, Header, Input, Static, Button
from .components.message import Message
from textual import work, on, log
from interfaces.fs import ProjectDirClass

class NewPitchScreen(Screen):
    """A simple chat interface screen."""
 
    CSS = """
    Screen {
        background: $surface;
    }
 
    #history {
        padding: 1 2;
        height: 1fr;
    }
 
    Message {
        width: 100%;
        margin-bottom: 1;
        layout: vertical;
    }
 
    Message .meta {
        margin-bottom: 0;
    }
 
    Message .body {
        padding: 1 2;
        width: auto;
        max-width: 70%;
    }
 
    /* User messages: right-aligned, accent colored */
    Message.user {
        align-horizontal: right;
    }
    Message.user .meta {
        text-align: right;
        color: $accent;
    }
    Message.user .body {
        background: $accent;
        color: $text;
    }
 
    /* Bot messages: left-aligned, panel colored */
    Message.bot {
        align-horizontal: left;
    }
    Message.bot .meta {
        color: $secondary;
    }
    Message.bot .body {
        background: $panel;
        color: $text;
    }
 
    #input-bar {
        height: auto;
        padding: 1 2;
        background: $boost;
    }
 
    #message-input {
        width: 1fr;
    }

    #gen-pitch{
      margin-right: 2;
      display: none;
    }

    #save-pitch{
      margin-left: 2;
      display: none;
    }

    #back-to-menu{
      margin-left: 2;
    }
    """
 
    # The fields brainstorm_pitch (PROMPT_PITCH) expects, in question order.
    PITCH_FIELDS = [
        "business_idea",
        "the_problem",
        "the_insight",
        "traction",
        "business_model",
        "the_team",
        "the_ask",
    ]
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+l", "clear", "Clear"),
    ]
    kernel = None
    project = {}
    current_pitch = ""
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield VerticalScroll(id="history")
        with Horizontal(id="input-bar"):
            # yield Input(placeholder="Type a message and press Enter…", id="message-input")
            yield Button("Generate Another Pitch", id="gen-pitch", variant="warning")
            yield Button("Save This Pitch", id="save-pitch", variant="success")
            yield Button("Back to Menu", id="back-to-menu", variant="primary")
        yield Footer()
 
    def on_mount(self) -> None:
        if not self._has_required_info():
            self._show_missing_info()
            return
        self.project = self.app.db.get_project(self.app.CURRENT_KERNEL_ID)

        self.kernel = bootstrap()
        self.title = "Create Pitches"
        self.sub_title = "Textual chat interface"
        self._add_message("Creating your business pitches now...", "bot")
        self.create_pitches()
        # self.reprompt_pitches()
        # self.query_one("#message-input", Input).focus()

    def _has_required_info(self) -> bool:
        """A pitch needs a selected project and the answered business questions."""
        log(self.app.business_answers)
        return (
            self.app.CURRENT_KERNEL_ID is not None
            and bool(getattr(self.app, "business_answers", None))
        )

    def _show_missing_info(self) -> None:
        self._add_message( "We need your Business Idea answers before we can create a pitch.", "bot")

    def _add_message(self, text: str, sender: str) -> None:
        history = self.query_one("#history", VerticalScroll)
        history.mount(Message(text, sender))
        history.scroll_end(animate=False)
 

  

    
    @work(exclusive=True)
    async def create_pitches(self) -> None:
        answers = getattr(self.app, "business_answers", {}) or {}
        data = {
            field: answers.get(field, "")
            for field in self.PITCH_FIELDS
        }

        # results = self.query_one("#pitch-results", VerticalScroll)
        try:
            result = await asyncio.to_thread(
                self.kernel.cmd, SysCommand.PROMPT_PITCH, **data
            )
        except Exception as error:  # kernel / model failure — show it instead of crashing
            self._add_message(f"Sorry, I couldn't create the pitches: {error}", "bot")
            return

        if result.code == Kernel.ExitCode.GOOD:
            self.current_pitch = result.data['response']
            self._add_message(f"{result.data['response']}", "bot")
            self.query_one("#gen-pitch").display = True
            self.query_one("#save-pitch").display = True
            # results.mount(Static(f"[b]2-Minute Verbal Pitch[/b]\n\n{result.data['two_minute_pitch']}"))
            # results.mount(Static(f"[b]10-Minute Narrative[/b]\n\n{result.data['ten_minute_pitch']}"))
            # results.mount(Static(f"[b]Email Pitch[/b]\n\n{result.data['email_pitch']}"))
            # results.mount(Static(f"[b]Pitch Scoring Card[/b]\n\n{result.data['scoring']}"))
        else:
            self._add_message("Something went wrong creating your pitches.", "bot")
            self.query_one("#gen-pitch").display = True






    @on(Button.Pressed, "#back-to-menu")
    def go_back_to_menu(self, event: Button.Pressed) -> None:
        self.dismiss()
    
    @on(Button.Pressed, "#gen-pitch")
    def gen_new_pitch(self, event: Button.Pressed) -> None:
        self._add_message("Generating your pitches...", 'bot')
        self.create_pitches()

    @on(Button.Pressed, "#save-pitch")
    def save_pitch(self, event: Button.Pressed) -> None:
        dl = ProjectDirClass(self.project['folder'])
        dl.create_directory("pitches")
        dl.write_file("pitches/pitch.md", self.current_pitch)
        self._add_message(f"I saved this version of the pitch here: {os.path.join(self.project['folder'], "pitches", "pitch.md")}. Next, let's generate your mockup website.", "bot")
        

    def action_clear(self) -> None:
        self.query_one("#history", VerticalScroll).remove_children()