import asyncio

from startupbuddykernel import bootstrap
from startupbuddykernel.kernel import Kernel, SysCommand

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static
from textual import on, work
from textual import log


class PitchScreen(Screen):
    """Generates the business pitches for the current kernel and displays them."""

    CSS = """
    PitchScreen {
        align: center middle;
    }

    #pitch-status {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding: 1;
    }

    #pitch-results {
        width: 100%;
        height: auto;
        max-height: 24;
        overflow-y: auto;
        padding: 1 2;
    }

    #pitch-results Static {
        margin-bottom: 1;
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

    kernel = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Creating your business pitches now...", id="pitch-status")
        yield VerticalScroll(id="pitch-results")
        yield Footer()

    def on_mount(self) -> None:
        if not self._has_required_info():
            self._show_missing_info()
            return
        self.kernel = bootstrap()
        self.create_pitches()

    def _has_required_info(self) -> bool:
        """A pitch needs a selected project and the answered business questions."""
        log(self.app.business_answers)
        return (
            self.app.CURRENT_KERNEL_ID is not None
            and bool(getattr(self.app, "business_answers", None))
        )

    def _show_missing_info(self) -> None:
        self.query_one("#pitch-status", Static).update(
            "We need your Business Idea answers before we can create a pitch."
        )
        results = self.query_one("#pitch-results", VerticalScroll)
        results.mount(
            Button("Back to Menu", id="back-to-menu", variant="primary")
        )

    @on(Button.Pressed, "#back-to-menu")
    def go_back_to_menu(self, event: Button.Pressed) -> None:
        self.dismiss()

    @work(exclusive=True)
    async def create_pitches(self) -> None:
        answers = getattr(self.app, "business_answers", {}) or {}
        data = {
            field: answers.get(field, "")
            for field in self.PITCH_FIELDS
        }

        results = self.query_one("#pitch-results", VerticalScroll)
        try:
            result = await asyncio.to_thread(
                self.kernel.cmd, SysCommand.PROMPT_PITCH, **data
            )
        except Exception as error:  # kernel / model failure — show it instead of crashing
            results.mount(Static(f"Sorry, I couldn't create the pitches: {error}"))
            return

        if result.code == Kernel.ExitCode.GOOD:
            results.mount(Static(f"{result.data['response']}"))
            # results.mount(Static(f"[b]2-Minute Verbal Pitch[/b]\n\n{result.data['two_minute_pitch']}"))
            # results.mount(Static(f"[b]10-Minute Narrative[/b]\n\n{result.data['ten_minute_pitch']}"))
            # results.mount(Static(f"[b]Email Pitch[/b]\n\n{result.data['email_pitch']}"))
            # results.mount(Static(f"[b]Pitch Scoring Card[/b]\n\n{result.data['scoring']}"))
        else:
            results.mount(Static(result.data.get("msg", "Something went wrong creating your pitches.")))
