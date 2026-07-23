from .databases import DBInterface
from .fs import ProjectDirClass


def parse_sections(markdown):
    sections = {}
    current = None
    lines = []
    for line in markdown.splitlines():
        if line.startswith('### '):
            if current is not None:
                sections[current] = '\n'.join(lines).strip()
            current = line[3:].strip()
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = '\n'.join(lines).strip()
    return sections