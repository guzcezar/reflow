""".NET (C# e VB.NET): análise textual por linha, a partir do código-fonte.

Sem compilador na stdlib, o parse é heurístico: os `using`/`Imports` do arquivo dizem quais
bibliotecas de UI ele usa e cada linha é casada contra padrões de UI, HTTP, banco, arquivos e
credenciais. No máximo um fato por linha. Binários (.exe/.dll) precisam ser decompilados antes
(ex.: ILSpy).
"""

import re
from pathlib import Path, PurePosixPath

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
    find_urls,
    is_connection_string,
    mask_secrets,
)

IGNORED_DIRS = {"bin", "obj", "packages", ".vs", ".git", "node_modules", "TestResults"}
SOURCE_SUFFIXES = {".cs", ".vb"}
PROJECT_SUFFIXES = {".csproj", ".vbproj"}
MAX_TARGET = 200

USING = re.compile(r"^\s*(?:using|Imports)\s+(?:static\s+)?(?:\w+\s*=\s*)?([\w.]+)\s*;?\s*$")
STRING = re.compile(r'\$?@?"((?:[^"\\\n]|\\.)*)"')
COMMENT_PREFIXES = ("//", "/*", "*", "'", "#region", "#endregion")
ENTRYPOINT = re.compile(
    r"\bstatic\s+(?:async\s+)?(?:void|int|Task(?:<int>)?)\s+Main\s*\(|^\s*(?:Public\s+)?(?:Shared\s+)?Sub\s+Main\s*\(",
    re.IGNORECASE,
)

UI_NAMESPACES = {
    "OpenQA.Selenium": "selenium",
    "Microsoft.Playwright": "playwright",
    "FlaUI": "flaui",
    "TestStack.White": "white",
    "System.Windows.Automation": "uiautomation",
    "WindowsInput": "inputsimulator",
    "AutoIt": "autoit",
    "SAPFEWSELib": "sapgui",
    "HtmlAgilityPack": "htmlagilitypack",  # raspagem de HTML: critério C3 da rubrica
    "AngleSharp": "anglesharp",
}
# Só valem em arquivos que importam uma biblioteca de UI.
UI_METHODS = re.compile(
    r"\.(FindElements?\w*|Click|DoubleClick|RightClick|SendKeys|Submit|GoToUrl|Navigate|SwitchTo|ExecuteScript"
    r"|SelectBy(?:Text|Value|Index)|GotoAsync|ClickAsync|DblClickAsync|FillAsync|TypeAsync|PressAsync|CheckAsync"
    r"|SelectOptionAsync|Locator|QuerySelector(?:All)?(?:Async)?|WaitForSelectorAsync|InnerTextAsync"
    r"|FindFirst\w*|FindAll\w*|GetMainWindow|AsButton|AsTextBox|AsComboBox|Enter|Invoke|GetCurrentPattern"
    r"|TextEntry|KeyPress|ModifiedKeyStroke|LeftButtonClick|MoveMouseTo|SelectNodes|SelectSingleNode|LoadHtml)\s*\("
)
# Interação de UI independente dos imports: (padrão, tech).
ALWAYS_UI = [
    (re.compile(r"\bSendKeys\.Send(?:Wait)?(?=\s*\()"), "winforms"),
    (
        re.compile(
            r"\b(?:FindWindow(?:Ex)?|SetForegroundWindow|SetCursorPos|mouse_event|keybd_event|SendInput)(?=\s*\()"
        ),
        "win32",
    ),
    (re.compile(r"\.findById(?=\s*\()"), "sapgui"),
    (re.compile(r"\bAutoItX3?\.\w+(?=\s*\()"), "autoit"),
    (
        re.compile(
            r"(?i:new)\s+(?:Chrome|Firefox|Edge|InternetExplorer|Remote(?:Web)?)Driver(?=\s*\()"
        ),
        "selenium",
    ),
]
DECLARATION = re.compile(
    r"\b(?:extern|Declare|Function)\b"
)  # assinaturas P/Invoke não são chamadas

HTTP_CLIENT = re.compile(
    r"\.(Get|Post|Put|Patch|Delete)(?:Async|StringAsync|ByteArrayAsync|StreamAsync|AsJsonAsync|FromJsonAsync)\s*\("
)
HTTP_OTHER = [
    (re.compile(r"(?i:new)\s+HttpRequestMessage\s*\("), "HttpClient"),
    (
        re.compile(r"\.(Download|Upload)(?:String|Data|File|Values)(?:Async|TaskAsync)?\s*\("),
        "WebClient",
    ),
    (re.compile(r"\b(?:Http)?WebRequest\.Create\s*\("), "WebRequest"),
    (re.compile(r"(?i:new)\s+RestRequest\s*\("), "RestSharp"),
]
HTTP_VERB = re.compile(r"\b(?:HttpMethod|Method)\.(\w+)")

DB_CLASSES = {
    "SqlConnection": "sqlserver", "OracleConnection": "oracle", "NpgsqlConnection": "postgres",
    "MySqlConnection": "mysql", "SQLiteConnection": "sqlite", "SqliteConnection": "sqlite",
    "OleDbConnection": "database", "OdbcConnection": "database",
}  # fmt: skip
DB_NEW = re.compile(r"(?i:new)\s+(" + "|".join(DB_CLASSES) + r")\s*\(")
EXCEL_API = re.compile(
    r"Workbooks\.Open\s*\(|(?i:new)\s+(?:ExcelPackage|XLWorkbook|XSSFWorkbook|HSSFWorkbook)\s*\(|ExcelReaderFactory\."
)
DATA_FILE = re.compile(r"\.(csv|xlsx|xlsm|xls)$", re.IGNORECASE)

ENV_VAR = re.compile(r'Environment\.GetEnvironmentVariable\s*\(\s*"([^"]+)"')
CONFIG_READ = re.compile(r'(?:AppSettings|Configuration|config)\s*[\[(]\s*"([^"]+)"', re.IGNORECASE)
HARDCODED = re.compile(r'\b(\w+)\s*(?:As\s+String\s*)?=\s*\$?@?"[^"]+"')
NETWORK_CREDENTIAL = re.compile(r"(?i:new)\s+NetworkCredential\s*\(")
CREDENTIAL_STORE = re.compile(r"\b(?:CredentialManager|CredRead)\b")
PROCESS_START = re.compile(
    r'Process\.Start\s*\(\s*(?:(?i:new)\s+ProcessStartInfo\s*\(\s*)?@?"([^"]+)"'
)

PACKAGE_REFERENCE = re.compile(r'<PackageReference\s+Include="([^"]+)"(?:\s+Version="([^"]+)")?')
PACKAGES_CONFIG = re.compile(r'<package\s+id="([^"]+)"\s+version="([^"]+)"')
ASSEMBLY_REFERENCE = re.compile(r'<Reference\s+Include="([^",]+)')
PROJECT_REFERENCE = re.compile(r'<ProjectReference\s+Include="([^"]+)"')
CONFIG_KEY = re.compile(
    r'(?:key|name)="([^"]+)"\s+(?:value|connectionString)="[^"]|"([^"]+)"\s*:\s*"[^"]'
)


def _project_files(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and not IGNORED_DIRS.intersection(p.relative_to(root).parts)
    )


def _is_config(path: Path) -> bool:
    name = path.name.lower()
    return path.suffix.lower() == ".config" or (
        name.startswith("appsettings") and name.endswith(".json")
    )


def _first(literals: list[str]) -> str:
    return literals[0][:MAX_TARGET] if literals else ""


class DotNetExtractor:
    name = "dotnet"

    def detect(self, root: Path) -> bool:
        return any(
            p.suffix.lower() in SOURCE_SUFFIXES | PROJECT_SUFFIXES for p in _project_files(root)
        )

    def extract(self, root: Path) -> Inventory:
        inventory = Inventory(source_type=self.name, project_name=root.name)
        dependencies: set[str] = set()

        for path in _project_files(root):
            relative = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            inventory.files.append(SourceFile(relative, file_kind(path.name), text.count("\n") + 1))
            suffix = path.suffix.lower()
            if suffix in SOURCE_SUFFIXES:
                _FileScanner(inventory, relative, text).scan()
            elif suffix in PROJECT_SUFFIXES or path.name.lower() == "packages.config":
                dependencies |= self._dependencies(inventory, root, path, text)
            if _is_config(path):
                self._config(inventory, relative, text)

        if not inventory.entrypoints:  # top-level statements (C# 9+) não têm Main
            inventory.entrypoints = [
                f.path for f in inventory.files if PurePosixPath(f.path).name == "Program.cs"
            ]
        inventory.dependencies = sorted(dependencies)
        return inventory

    def _dependencies(self, inventory: Inventory, root: Path, path: Path, text: str) -> set[str]:
        found = {
            f"{name}@{version}" if version else name
            for name, version in PACKAGE_REFERENCE.findall(text)
        }
        found |= {f"{name}@{version}" for name, version in PACKAGES_CONFIG.findall(text)}
        found |= {
            name
            for name in ASSEMBLY_REFERENCE.findall(text)
            if not name.startswith(("System", "Microsoft.CSharp", "mscorlib"))
        }
        for include in PROJECT_REFERENCE.findall(text):
            target = (path.parent / include.replace("\\", "/")).resolve()
            ref = (
                target.relative_to(root.resolve()).as_posix()
                if target.is_relative_to(root.resolve())
                else include
            )
            inventory.call_graph.append(CallEdge(path.relative_to(root).as_posix(), ref))
        return found

    def _config(self, inventory: Inventory, path: str, text: str) -> None:
        for number, line in enumerate(text.splitlines(), start=1):
            connection = next((s for s in STRING.findall(line) if is_connection_string(s)), None)
            if connection:
                value = mask_secrets(connection)
                inventory.data_sources.append(DataSource(path, number, database_kind(value), value))
                continue
            match = CONFIG_KEY.search(line)
            key = match and (match.group(1) or match.group(2))
            if key and SECRET_NAME.search(key):
                inventory.credentials.append(Credential(path, number, f"config:{key}"))


class _FileScanner:
    def __init__(self, inventory: Inventory, path: str, text: str):
        self.inventory = inventory
        self.path = path
        self.lines = text.splitlines()
        imports = {m.group(1) for line in self.lines if (m := USING.match(line))}
        self.ui_libs = sorted(
            {
                tech
                for ns, tech in UI_NAMESPACES.items()
                for imp in imports
                if imp == ns or imp.startswith(ns + ".")
            }
        )
        self.uses_http_client = "HttpClient" in text

    def scan(self) -> None:
        for number, raw in enumerate(self.lines, start=1):
            line = raw.strip()
            if not line or line.startswith(COMMENT_PREFIXES) or USING.match(raw):
                continue
            raw_literals = STRING.findall(line)
            literals = [mask_secrets(s) for s in raw_literals]
            if ENTRYPOINT.search(line):
                self.inventory.entrypoints.append(self.path)
            self._credentials(number, line)
            (
                self._ui(number, line, literals)
                or self._http(number, line, literals)
                or self._data(number, line, raw_literals)
                or self._process(number, line)
            )

    def _ui(self, number: int, line: str, literals: list[str]) -> bool:
        if not DECLARATION.search(line):
            for pattern, tech in ALWAYS_UI:
                if match := pattern.search(line):
                    action = re.sub(r"\s+", " ", match.group(0)).lstrip(".")
                    return self._add_ui(number, tech, action, literals)
        methods = UI_METHODS.findall(line)
        if self.ui_libs and methods:
            return self._add_ui(number, self.ui_libs[0], ".".join(methods), literals)
        return False

    def _add_ui(self, number: int, tech: str, action: str, literals: list[str]) -> bool:
        self.inventory.ui_interactions.append(
            UiInteraction(self.path, number, tech, action, _first(literals))
        )
        return True

    def _http(self, number: int, line: str, literals: list[str]) -> bool:
        url = next((u for s in literals for u in find_urls(s)), _first(literals))
        verb = HTTP_VERB.search(line)
        if self.uses_http_client and (match := HTTP_CLIENT.search(line)):
            self.inventory.http_calls.append(
                HttpCall(self.path, number, match.group(1).upper(), url, "HttpClient")
            )
            return True
        for pattern, lib in HTTP_OTHER:
            if match := pattern.search(line):
                if lib == "WebClient":
                    method = "GET" if match.group(1) == "Download" else "POST"
                else:
                    method = (
                        verb.group(1).upper()
                        if verb
                        else ("GET" if lib == "RestSharp" else "REQUEST")
                    )
                self.inventory.http_calls.append(HttpCall(self.path, number, method, url, lib))
                return True
        return False

    def _data(self, number: int, line: str, raw_literals: list[str]) -> bool:
        connection = next((s for s in raw_literals if is_connection_string(s)), None)
        if match := DB_NEW.search(line):
            ref = mask_secrets(connection) if connection else _first(raw_literals)
            return self._add_data(number, DB_CLASSES[match.group(1)], ref)
        if connection:
            value = mask_secrets(connection)
            return self._add_data(number, database_kind(value), value)
        data_file = next((s for s in raw_literals if DATA_FILE.search(s)), None)
        if EXCEL_API.search(line):
            return self._add_data(number, "excel", data_file or _first(raw_literals))
        if data_file:
            kind = "csv" if data_file.lower().endswith(".csv") else "excel"
            return self._add_data(number, kind, data_file)
        return False

    def _add_data(self, number: int, kind: str, ref: str) -> bool:
        self.inventory.data_sources.append(DataSource(self.path, number, kind, mask_secrets(ref)))
        return True

    def _process(self, number: int, line: str) -> bool:
        if match := PROCESS_START.search(line):
            self.inventory.call_graph.append(CallEdge(self.path, match.group(1)))
            return True
        return False

    def _credentials(self, number: int, line: str) -> None:
        refs = [f"env:{name}" for name in ENV_VAR.findall(line)]
        refs += [f"config:{key}" for key in CONFIG_READ.findall(line) if SECRET_NAME.search(key)]
        refs += [
            f"{name} (valor hardcoded)"
            for name in HARDCODED.findall(line)
            if SECRET_NAME.search(name)
        ]
        if NETWORK_CREDENTIAL.search(line):
            refs.append("NetworkCredential" + (" (valor hardcoded)" if STRING.search(line) else ""))
        if CREDENTIAL_STORE.search(line):
            refs.append(f"credman:{_first(STRING.findall(line))}")
        for ref in refs:
            self.inventory.credentials.append(Credential(self.path, number, ref))
