from pathlib import Path
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static, Header, Input, DirectoryTree
from textual import on

class NewScreen(Screen):
    selected_folder = None

    def compose(self) -> ComposeResult:
      yield Header()
      yield Static("What is the name of this project?")
      yield Input(id="project-name")
      yield Static("Select a folder for this project:")
      yield DirectoryTree(str(Path.home()), id="project-folder")
      yield Static("", id="status")

    @on(DirectoryTree.DirectorySelected)
    def folder_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        self.selected_folder = str(event.path)
        self.query_one("#status", Static).update("")

    @on(Input.Submitted)
    def save_project_name(self, event: Input.Submitted):
        if self.selected_folder is None:
            self.query_one("#status", Static).update("Please select a folder before continuing.")
            return
        self.dismiss({"name": event.value, "folder": self.selected_folder})
