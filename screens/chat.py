import asyncio

from textual.screen import Screen
from startupbuddykernel import bootstrap
from startupbuddykernel.kernel import Kernel, SysCommand
from datetime import datetime
 
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Footer, Header, Input, Static
from .components.message import Message
from textual import work

class ChatScreen(Screen):
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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield VerticalScroll(id="history")
        with Horizontal(id="input-bar"):
            yield Input(placeholder="Type a message and press Enter…", id="message-input")
        yield Footer()
 
    def on_mount(self) -> None:
        self.kernel = bootstrap()

        self.title = "Chat"
        self.sub_title = "Textual chat interface"
        self._add_message("Hi there! Type something below to get started.", "bot")
        self.query_one("#message-input", Input).focus()
 
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
        self.first_prompt(text)
        self.prompt_loop()

    @work(exclusive=True)
    async def first_prompt(self, text):
        result = await asyncio.to_thread(self.kernel.cmd, SysCommand.KERNEL_PROMPT, prompt=text, project_directory="/Users/shariqtorres/Documents/Gitea/kclikernel/tests/proj")
        if result.code == Kernel.ExitCode.GOOD:
            self._add_message(f"{result.data['response']}", "bot")
            if len(result.data['tools']) > 0:
                tool_results = await asyncio.to_thread(self.kernel.cmd, SysCommand.TOOL_CALL, tools=result.data['tools'])
                if tool_results.code == Kernel.ExitCode.GOOD:
                    for r in tool_results.data['result']:
                        self._add_message(f"Calling {r['tool']} with these arguments: {r['arguments']}", "bot")


    @work(exclusive=True)     
    async def prompt_loop(self):
      while True:
          result = await asyncio.to_thread(self.kernel.cmd, SysCommand.REPROMPT, project_directory="/Users/shariqtorres/Documents/Gitea/kclikernel/tests/proj")
          if result.code == Kernel.ExitCode.GOOD:
              self._add_message(f"{result.data['response']}", "bot")
              if len(result.data['tools']) > 0:
                  tool_results = await asyncio.to_thread(self.kernel.cmd, SysCommand.TOOL_CALL, tools=result.data['tools'])
                  if tool_results.code == Kernel.ExitCode.GOOD:
                      for r in tool_results.data['result']:
                          self._add_message(f"Calling {r['tool']} with these arguments: {r['arguments']}", "bot")
                      continue
              else:
                  break
              return True


    def action_clear(self) -> None:
        self.query_one("#history", VerticalScroll).remove_children()