"""Automation Anywhere A360: bots exportados em JSON (pasta descompactada ou .zip).

O parse é tolerante: depende só de `packageName`, `commandName` e da árvore de nodes.
Todo o resto é lido como texto bruto. O schema do A360 varia por versão de package.
"""

import json
import zipfile
from collections.abc import Iterator
from pathlib import Path, PurePosixPath
from typing import Any

from reflow.inventory import (
    CallEdge,
    Credential,
    DataSource,
    HttpCall,
    Inventory,
    SourceFile,
    UiInteraction,
)
from reflow.patterns import database_kind, find_urls, mask_secrets

UI_PACKAGES = {
    "recorder", "universalrecorder", "browser", "window", "mouse", "keystrokes",
    "simulatekeystrokes", "imagerecognition", "ocr", "terminalemulator", "screen",
    "application", "sapgui", "citrix",
}  # fmt: skip
HTTP_PACKAGES = {"restwebservices", "rest", "soapwebservice", "soap"}
FILE_PACKAGES = {"excel": "excel", "csv": "csv", "file": "file", "folder": "file", "pdf": "file"}
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
MAX_TARGET = 200


def _key(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def _strings(value: Any) -> Iterator[str]:
    """Valores textuais de atributos, ignorando metadados (`name`, `type`) e credenciais."""
    if isinstance(value, str):
        if value.strip():
            yield value
    elif isinstance(value, dict):
        if str(value.get("type", "")).upper() == "CREDENTIAL":
            return
        if "value" in value:
            yield from _strings(value["value"])
            return
        for key, item in value.items():
            if key not in {"name", "type"}:
                yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _credentials(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        if str(value.get("type", "")).upper() == "CREDENTIAL":
            yield "/".join(s for s in _all_strings(value) if s.upper() != "CREDENTIAL")
            return
        for item in value.values():
            yield from _credentials(item)
    elif isinstance(value, list):
        for item in value:
            yield from _credentials(item)


def _all_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict | list):
        for item in value.values() if isinstance(value, dict) else value:
            yield from _all_strings(item)


def _nodes(value: Any) -> Iterator[dict]:
    """Percorre a árvore em pré-ordem, na mesma ordem das linhas do editor do A360."""
    if isinstance(value, list):
        for item in value:
            yield from _nodes(item)
    elif isinstance(value, dict):
        if "commandName" in value:
            yield value
        for key, item in value.items():
            if key != "attributes":
                yield from _nodes(item)


def _read_bots(root: Path) -> Iterator[tuple[str, dict]]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                for name in sorted(archive.namelist()):
                    bot = _parse(archive.read(name))
                    if bot is not None:
                        yield f"{path.relative_to(root).as_posix()}!/{name}", bot
        elif path.is_file() and path.suffix.lower() in {"", ".json"}:
            bot = _parse(path.read_bytes())
            if bot is not None:
                yield path.relative_to(root).as_posix(), bot


def _parse(raw: bytes) -> dict | None:
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if isinstance(data, dict) and isinstance(data.get("nodes"), list):
        return data
    return None


def _bot_basename(ref: str) -> str:
    return PurePosixPath(ref.replace("\\", "/").split("!/")[-1]).stem.lower()


class A360Extractor:
    name = "a360"

    def detect(self, root: Path) -> bool:
        return next(_read_bots(root), None) is not None

    def extract(self, root: Path) -> Inventory:
        inventory = Inventory(source_type=self.name, project_name=root.name)
        packages: dict[str, str] = {}  # nome -> versão declarada ("" se desconhecida)

        for bot_name, bot in _read_bots(root):
            nodes = list(_nodes(bot["nodes"]))
            inventory.files.append(SourceFile(bot_name, "bot", len(nodes)))
            for line, node in enumerate(nodes, start=1):
                packages.setdefault(str(node.get("packageName", "")), "")
                self._collect(inventory, bot_name, line, node)
            for declared in bot.get("packages") or []:
                if isinstance(declared, dict) and declared.get("name"):
                    packages[str(declared["name"])] = str(declared.get("version", ""))

        packages.pop("", None)
        inventory.dependencies = sorted(
            f"a360:{name}@{version}" if version else f"a360:{name}"
            for name, version in packages.items()
        )
        called = {_bot_basename(edge.target) for edge in inventory.call_graph}
        inventory.entrypoints = [
            f.path for f in inventory.files if _bot_basename(f.path) not in called
        ]
        return inventory

    def _collect(self, inventory: Inventory, bot: str, line: int, node: dict) -> None:
        package = str(node.get("packageName", ""))
        command = str(node.get("commandName", ""))
        attributes = node.get("attributes", [])
        texts = [mask_secrets(s) for s in _strings(attributes)]
        urls = [u for s in _strings(attributes) for u in find_urls(s)]
        key = _key(package)

        for ref in _credentials(attributes):
            inventory.credentials.append(Credential(bot, line, ref))

        if key in UI_PACKAGES:
            target = urls[0] if urls else (texts[0] if texts else "")
            inventory.ui_interactions.append(
                UiInteraction(bot, line, f"a360:{package}", command, target[:MAX_TARGET])
            )
        elif key in HTTP_PACKAGES:
            method = command.upper() if command.lower() in HTTP_METHODS else command
            inventory.http_calls.append(
                HttpCall(bot, line, method, urls[0] if urls else "", f"a360:{package}")
            )
        elif key == "database" and command.lower() == "connect":
            ref = next((t for t in texts if "=" in t or "://" in t), texts[0] if texts else "")
            inventory.data_sources.append(DataSource(bot, line, database_kind(ref), ref))
        elif key == "taskbot" and command.lower() == "run":
            target = next((t for t in texts if "/" in t or "\\" in t), texts[0] if texts else "")
            inventory.call_graph.append(CallEdge(bot, target))
        else:
            kind = next((v for k, v in FILE_PACKAGES.items() if key.startswith(k)), None)
            path = next((t for t in texts if "\\" in t or "/" in t), None)
            if kind and path:
                inventory.data_sources.append(DataSource(bot, line, kind, path))
