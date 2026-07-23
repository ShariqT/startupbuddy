import asyncio

from textual.screen import Screen, ModalScreen
from startupbuddykernel import bootstrap
from startupbuddykernel.kernel import Kernel, SysCommand
from datetime import datetime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Static
from .components.message import Message
from textual import on, work


class PitchPromptModal(ModalScreen):
    """Confirmation modal shown once all business questions are answered."""

    CSS = """
    PitchPromptModal {
        align: center middle;
    }

    #modal-dialog {
        width: 80%;
        max-width: 100;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #modal-message {
        text-align: center;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-dialog"):
            yield Static(
                "Thanks for the information. The next step is to generate the pitch",
                id="modal-message",
            )
            yield Button("Continue", id="modal-continue", variant="primary")

    @on(Button.Pressed, "#modal-continue")
    def continue_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class QuestionScreen(Screen):
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
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+l", "clear", "Clear"),
    ]
    kernel = None
    project_directory = None
    answers: reactive[list] = reactive(list)
    qcount: reactive[int] = reactive(0)
    BUSINESS_KEYS = [
        "business_idea", "the_problem", "the_insight", "traction",
        "business_model", "the_team", "the_ask",
    ]
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield VerticalScroll(id="history")
        with Horizontal(id="input-bar"):
            yield Input(placeholder="Type a message and press Enter…", id="message-input")
        yield Footer()

    def on_mount(self) -> None:
        self.kernel = bootstrap()
        self.qcount = 0

        project = self.app.db.get_project(self.app.CURRENT_KERNEL_ID)
        self.project_directory = project.get("folder") if project else None

        business_answers = project.get("business_answers") if project else None
        if business_answers:
            self.answers = [business_answers.get(key, "") for key in self.BUSINESS_KEYS]

        self.title = "The Business Idea"
        self.sub_title = "Let's flesh out the business behind the kernel"
        self._add_message("I'm going to ask you a few questions to undestand more about your business idea. At the end of this, I will give you some pitches that you can use in-person or in email. Feel free to edit them to make them sound natural TO YOU. This is just a starting point.", "bot")
        self._add_message("What does your company do? (2 sentences max — this becomes the opening)", "bot")
        self.query_one("#message-input", Input).focus()
        self._prefill_input()

    def watch_qcount(self, old_count, new_count):
        if new_count == 1:
            self._add_message("What problem are you solving and for whom?", "bot")
        if new_count == 2:
            self._add_message("What's your unique insight? (What do you know that others don't?)", "bot")
        if new_count == 3:
            self._add_message("What traction do you have? (users, revenue, growth rate — with timeframes). If none: say so honestly, we'll build the pitch around insight and team instead.", "bot")
        if new_count == 4:
            self._add_message("What's your business model? (one sentence — how do you make money?)", "bot")
        if new_count == 5:
            self._add_message("Who's on the team? (names, roles, key accomplishments — not titles)", "bot")
        if new_count == 6:
            self._add_message("What are you asking for? (how much are you raising, and what will it unlock?)", "bot")
        if new_count == 7:
            self.app.push_screen(PitchPromptModal(), self._pitch_prompt_dismissed)
            return
        self._prefill_input()

    def _pitch_prompt_dismissed(self, result) -> None:
        # Dismissing the modal returns the collected answers via the questions
        # screen's callback (business_questions_answered), which saves them and
        # routes the user to the MenuScreen.
        self.dismiss(self.answers)

    def _prefill_input(self) -> None:
        idx = self.qcount
        if 0 <= idx < len(self.answers):
            self.query_one("#message-input", Input).value = self.answers[idx]

    def _add_message(self, text: str, sender: str) -> None:
        history = self.query_one("#history", VerticalScroll)
        history.mount(Message(text, sender))
        history.scroll_end(animate=False)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.value = ""
        self._add_message(text, "user")
        idx = self.qcount
        if idx < len(self.answers):
            self.answers[idx] = text
        else:
            self.answers.append(text)
        self.qcount = self.qcount + 1



    def action_clear(self) -> None:
        self.query_one("#history", VerticalScroll).remove_children()
