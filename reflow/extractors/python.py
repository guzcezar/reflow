"""Projetos Python: análise estática via AST (imports, chamadas e literais)."""

import ast
import re
import sys
import tomllib
from pathlib import Path

from reflow.inventory import (
    CallEdge,
    Credential,
    DataSource,
    HttpCall,
    Inventory,
    SourceFile,
    UiInteraction,
)
from reflow.patterns import (
    SECRET_NAME,
    database_kind,
    file_kind,
    is_connection_string,
    mask_secrets,
)

IGNORED_DIRS = {".venv", "venv", "env", "__pycache__", ".git", "site-packages", "node_modules"}

UI_LIBS = {
    "selenium", "pyautogui", "pywinauto", "playwright", "pynput", "uiautomation",
    "keyboard", "mouse", "botcity", "rpa", "autoit", "win32gui", "sapgui",
    "bs4",  # raspagem de HTML: critério C3 da rubrica
}  # fmt: skip
# Fallback para objetos de origem desconhecida (ex.: `driver` recebido por parâmetro):
# só métodos que não existem fora de bibliotecas de UI.
UI_ONLY_METHODS = {
    "click", "double_click", "right_click", "send_keys", "type_keys", "typewrite", "hotkey",
    "find_element", "find_elements", "select_option", "locateonscreen", "locatecenteronscreen",
    "child_window", "set_focus", "set_text", "execute_script",
}  # fmt: skip
HTTP_LIBS = {"requests", "httpx", "urllib", "urllib3", "aiohttp", "zeep", "suds"}
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "request", "urlopen"}
DB_LIBS = {
    "pyodbc": "database", "pymssql": "sqlserver", "cx_oracle": "oracle", "oracledb": "oracle",
    "psycopg2": "postgres", "psycopg": "postgres", "pymysql": "mysql", "mysql": "mysql",
    "sqlite3": "sqlite", "sqlalchemy": "database",
}  # fmt: skip
PANDAS_IO = {"read_csv": "csv", "to_csv": "csv", "read_excel": "excel", "to_excel": "excel"}
EXCEL_CALLS = {"load_workbook", "open_workbook"}
REQUIREMENT = re.compile(r"^\s*([A-Za-z0-9_.\-]+(\[.*\])?\s*([<>=!~]=?\s*[^;#\s]+)?)")


def _dotted(node: ast.AST) -> list[str]:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    elif isinstance(node, ast.Call):
        parts.extend(reversed(_dotted(node.func)))
    return list(reversed(parts))


def _arg(call: ast.Call, index: int = 0, *keywords: str) -> str:
    """Argumento posicional `index` ou keyword equivalente, como texto com secrets mascarados."""
    candidates = list(call.args[index : index + 1])
    candidates += [k.value for k in call.keywords if k.arg in keywords]
    if not candidates:
        return ""
    value = candidates[0]
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return mask_secrets(value.value)
    return mask_secrets(ast.unparse(value))


def _all_args(call: ast.Call) -> str:
    return mask_secrets(", ".join(ast.unparse(a) for a in [*call.args, *call.keywords]))


class _FileVisitor(ast.NodeVisitor):
    def __init__(self, inventory: Inventory, path: str, local_modules: dict[str, str]):
        self.inventory = inventory
        self.path = path
        self.local_modules = local_modules
        self.aliases: dict[str, str] = {}  # nome local -> lib raiz
        self.objects: dict[str, str] = {}  # variável -> lib raiz que a criou (driver, session...)
        self.imported: set[str] = set()

    @property
    def ui_lib(self) -> str | None:
        """Lib de UI interativa importada no arquivo (raspagem de HTML não clica em nada)."""
        return next((lib for lib in sorted(self.imported) if lib in UI_LIBS - {"bs4"}), None)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0].lower()
            self._register(alias.name, root, alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        root = module.split(".")[0].lower()
        if node.level == 0 and module:
            for alias in node.names:
                self._register(module, root, alias.asname or alias.name)
        for alias in node.names:
            self._link(f"{module}.{alias.name}" if module else alias.name)

    def _register(self, module: str, root: str, local_name: str) -> None:
        self.aliases[local_name] = root
        self.imported.add(root)
        self._link(module)

    def _link(self, module: str) -> None:
        target = self.local_modules.get(module) or self.local_modules.get(module.rsplit(".", 1)[0])
        if target and target != self.path:
            edge = CallEdge(self.path, target)
            if edge not in self.inventory.call_graph:
                self.inventory.call_graph.append(edge)

    def visit_If(self, node: ast.If) -> None:
        if "__name__" in ast.unparse(node.test) and "__main__" in ast.unparse(node.test):
            self.inventory.entrypoints.append(self.path)
        self.generic_visit(node)

    def _origin(self, node: ast.AST) -> str:
        """Lib raiz de uma expressão: `requests.Session()` -> requests, `driver.x()` -> selenium."""
        parts = _dotted(node.func if isinstance(node, ast.Call) else node)
        if not parts:
            return ""
        return self.aliases.get(parts[0]) or self.objects.get(parts[0], "")

    def _track(self, targets: list[ast.expr], value: ast.AST) -> None:
        origin = self._origin(value)
        if origin:
            for target in targets:
                for name in ast.walk(target):
                    if isinstance(name, ast.Name):
                        self.objects[name.id] = origin

    def visit_For(self, node: ast.For) -> None:
        self._track([node.target], node.iter)
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            if item.optional_vars is not None:
                self._track([item.optional_vars], item.context_expr)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        value = node.value
        self._track(node.targets, value)
        if isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value:
            for target in node.targets:
                if isinstance(target, ast.Name) and SECRET_NAME.search(target.id):
                    self._credential(node.lineno, f"{target.id} (valor hardcoded)")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and is_connection_string(node.value):
            value = mask_secrets(node.value)
            self.inventory.data_sources.append(
                DataSource(self.path, node.lineno, database_kind(value), value)
            )

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if _dotted(node.value)[-2:] == ["os", "environ"]:
            self._credential(node.lineno, f"env:{ast.unparse(node.slice).strip(chr(39) + chr(34))}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        parts = _dotted(node.func)
        if parts:
            self._classify_call(node, parts)
        self.generic_visit(node)

    def _classify_call(self, node: ast.Call, parts: list[str]) -> None:
        root = self._origin(node)
        method = parts[-1].lower()
        line = node.lineno

        if parts[-2:] in (["os", "getenv"], ["environ", "get"]):
            self._credential(line, f"env:{_arg(node).strip(chr(39) + chr(34))}")
        elif root == "keyring":
            self._credential(line, f"keyring:{ast.unparse(node)}")
        elif root in HTTP_LIBS and method in HTTP_METHODS:
            if method == "request":
                verb, url = _arg(node, 0, "method"), _arg(node, 1, "url")
            else:
                verb, url = method.upper(), _arg(node, 0, "url")
            self.inventory.http_calls.append(HttpCall(self.path, line, verb, url, root))
        elif root in DB_LIBS and method in {"connect", "create_engine"}:
            ref = _arg(node)
            kind = DB_LIBS[root] if DB_LIBS[root] != "database" else database_kind(ref)
            self.inventory.data_sources.append(DataSource(self.path, line, kind, ref))
        elif method in PANDAS_IO:
            ref = _arg(node, 0, "path_or_buf", "io", "excel_writer")
            self.inventory.data_sources.append(DataSource(self.path, line, PANDAS_IO[method], ref))
        elif method in EXCEL_CALLS:
            ref = _arg(node, 0, "filename")
            self.inventory.data_sources.append(DataSource(self.path, line, "excel", ref))
        elif root in UI_LIBS or (not root and self.ui_lib and method in UI_ONLY_METHODS):
            tech = root if root in UI_LIBS else self.ui_lib
            self.inventory.ui_interactions.append(
                UiInteraction(self.path, line, tech, ".".join(parts[-2:]), _all_args(node))
            )

    def _credential(self, line: int, ref: str) -> None:
        self.inventory.credentials.append(Credential(self.path, line, ref))


def _project_files(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and not IGNORED_DIRS.intersection(p.relative_to(root).parts)
    )


def _module_name(relative: Path) -> str:
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _declared_dependencies(root: Path) -> list[str]:
    deps: list[str] = []
    for req in sorted(root.rglob("requirements*.txt")):
        for line in req.read_text(encoding="utf-8", errors="replace").splitlines():
            match = REQUIREMENT.match(line)
            if match and not line.lstrip().startswith(("#", "-")):
                deps.append(match.group(1).replace(" ", ""))
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        deps.extend(data.get("project", {}).get("dependencies", []))
    return deps


class PythonExtractor:
    name = "python"

    def detect(self, root: Path) -> bool:
        return any(p.suffix == ".py" for p in _project_files(root))

    def extract(self, root: Path) -> Inventory:
        inventory = Inventory(source_type=self.name, project_name=root.name)
        files = _project_files(root)
        scripts = [p for p in files if p.suffix == ".py"]
        local_modules = {
            _module_name(p.relative_to(root)): p.relative_to(root).as_posix() for p in scripts
        }
        local_roots = {name.split(".")[0].lower() for name in local_modules}
        imported: set[str] = set()

        for path in files:
            relative = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8", errors="replace")
            inventory.files.append(SourceFile(relative, file_kind(path.name), text.count("\n") + 1))
            if path.suffix != ".py":
                continue
            try:
                tree = ast.parse(text, filename=relative)
            except SyntaxError:
                continue  # Python 2 ou arquivo quebrado: fica só no inventário de arquivos
            visitor = _FileVisitor(inventory, relative, local_modules)
            visitor.visit(tree)
            imported |= visitor.imported

        third_party = imported - local_roots - set(sys.stdlib_module_names)
        declared = _declared_dependencies(root)
        declared_roots = {
            re.split(r"[<>=!~\[;\s]", d)[0].lower().replace("-", "_") for d in declared
        }
        inventory.dependencies = sorted(
            set(declared) | {m for m in third_party if m.replace("-", "_") not in declared_roots}
        )
        return inventory
