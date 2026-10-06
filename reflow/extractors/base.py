from pathlib import Path
from typing import Protocol

from reflow.inventory import Inventory


class Extractor(Protocol):
    """Uma origem de código legado. Nova origem = novo módulo implementando esta interface."""

    name: str

    def detect(self, root: Path) -> bool: ...

    def extract(self, root: Path) -> Inventory: ...
