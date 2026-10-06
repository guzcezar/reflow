from pathlib import Path

from reflow.extractors.a360 import A360Extractor
from reflow.extractors.base import Extractor
from reflow.extractors.dotnet import DotNetExtractor
from reflow.extractors.python import PythonExtractor

# A ordem importa: a primeira origem detectada vence.
EXTRACTORS: list[Extractor] = [A360Extractor(), DotNetExtractor(), PythonExtractor()]


def find_extractor(root: Path) -> Extractor:
    for extractor in EXTRACTORS:
        if extractor.detect(root):
            return extractor
    names = ", ".join(e.name for e in EXTRACTORS)
    raise ValueError(f"Nenhuma origem suportada ({names}) detectada em {root}")
