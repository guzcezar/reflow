"""Contrato entre a extração (Python) e as fases de LLM (Claude): só fatos, nunca interpretação."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class SourceFile:
    path: str
    kind: str  # bot | script | config | data | other
    lines: int


@dataclass
class CallEdge:
    source: str
    target: str


@dataclass
class UiInteraction:
    """Interação com UI (web, desktop, terminal) ou raspagem de tela/HTML."""

    file: str
    line: int
    tech: str  # ex.: selenium, pyautogui, flaui, a360:Browser
    action: str
    target: str = ""


@dataclass
class HttpCall:
    file: str
    line: int
    method: str
    url: str
    lib: str


@dataclass
class DataSource:
    file: str
    line: int
    kind: str  # sqlserver | oracle | postgres | mysql | sqlite | excel | csv | file | database
    ref: str


@dataclass
class Credential:
    file: str
    line: int
    ref: str


@dataclass
class Inventory:
    source_type: str  # a360 | dotnet | python
    project_name: str
    files: list[SourceFile] = field(default_factory=list)
    entrypoints: list[str] = field(default_factory=list)
    call_graph: list[CallEdge] = field(default_factory=list)
    ui_interactions: list[UiInteraction] = field(default_factory=list)
    http_calls: list[HttpCall] = field(default_factory=list)
    data_sources: list[DataSource] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    credentials: list[Credential] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json() + "\n", encoding="utf-8")
