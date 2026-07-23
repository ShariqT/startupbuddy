from pathlib import Path


class ProjectDirClass:
    def __init__(self, project_path):
        self.root = Path(project_path)

    def create_directory(self, name):
        target = self.root / name
        target.mkdir(parents=True, exist_ok=True)
        return target

    def write_file(self, name, content):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return target

    def read_file(self, name):
        target = self.root / name
        return target.read_text()
