from textual.app import ComposeResult
from textual.widgets import Static
from datetime import datetime

class Message(Static):
    """A single chat bubble."""
 
    def __init__(self, text: str, sender: str) -> None:
        super().__init__()
        self.text = text
        self.sender = sender  # "user" or "bot"
 
    def compose(self) -> ComposeResult:
        stamp = datetime.now().strftime("%H:%M")
        yield Static(f"[b]{self.sender.title()}[/b] [dim]{stamp}[/dim]", classes="meta")
        yield Static(self.text, classes="body")
 
    def on_mount(self) -> None:
        self.add_class(self.sender)