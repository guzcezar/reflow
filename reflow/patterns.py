"""Heurísticas textuais compartilhadas pelos extractors: secrets, URLs e connection strings."""

import re

_SECRET_KV = re.compile(
    r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key|access[_-]?key)(\s*[=:]\s*)([^;&\s'\"]+)"
)
_URL_USERINFO = re.compile(r"(://[^/\s:@]+:)[^@\s/]+@")
_URL = re.compile(r"https?://[^\s'\"<>]+")

_DB_KINDS = [
    ("sqlserver", re.compile(r"(?i)sql\s*server|mssql|odbc driver \d+ for sql|initial catalog")),
    ("oracle", re.compile(r"(?i)oracle|\(description=")),
    ("postgres", re.compile(r"(?i)postgres")),
    ("mysql", re.compile(r"(?i)mysql")),
    ("sqlite", re.compile(r"(?i)sqlite")),
]
_CONNECTION_STRING = re.compile(
    r"(?i)(driver=|server=|data source=|initial catalog=|database=|"
    r"(mssql|postgresql|postgres|mysql|oracle|sqlite)(\+\w+)?://)"
)

SECRET_NAME = re.compile(r"(?i)(password|passwd|pwd|token|secret|api_?key|senha)")


def mask_secrets(text: str) -> str:
    """Remove valores de secrets, preservando a chave para o leitor saber que ali existe um."""
    text = _SECRET_KV.sub(r"\1\2***", text)
    return _URL_USERINFO.sub(r"\1***@", text)


def find_urls(text: str) -> list[str]:
    return [mask_secrets(url) for url in _URL.findall(text)]


def is_connection_string(text: str) -> bool:
    return bool(_CONNECTION_STRING.search(text))


def database_kind(text: str) -> str:
    for kind, pattern in _DB_KINDS:
        if pattern.search(text):
            return kind
    return "database"


def file_kind(name: str) -> str:
    suffix = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if suffix in {"py", "cs", "vb"}:
        return "script"
    if suffix in {
        "json",
        "yaml",
        "yml",
        "ini",
        "cfg",
        "toml",
        "env",
        "config",
        "xml",
        "csproj",
        "vbproj",
        "sln",
    }:
        return "config"
    if suffix in {"csv", "xlsx", "xls", "xlsm", "txt"}:
        return "data"
    return "other"
