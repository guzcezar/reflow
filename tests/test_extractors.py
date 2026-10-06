import json
import shutil
import zipfile
from pathlib import Path

import pytest

from reflow.cli import main
from reflow.extractors import find_extractor
from reflow.extractors.a360 import A360Extractor
from reflow.extractors.dotnet import DotNetExtractor
from reflow.extractors.python import PythonExtractor

FIXTURES = Path(__file__).parent / "fixtures"
A360_PROJECT = FIXTURES / "a360" / "conciliacao-nf"
PYTHON_PROJECT = FIXTURES / "python" / "consulta-portal"
DOTNET_PROJECT = FIXTURES / "dotnet" / "emissao-boleto"


def test_detects_source_type():
    assert find_extractor(A360_PROJECT).name == "a360"
    assert find_extractor(PYTHON_PROJECT).name == "python"
    assert find_extractor(DOTNET_PROJECT).name == "dotnet"


def test_unknown_source_raises(tmp_path):
    (tmp_path / "readme.md").write_text("nada aqui")
    with pytest.raises(ValueError):
        find_extractor(tmp_path)


class TestA360:
    inventory = A360Extractor().extract(A360_PROJECT)

    def test_bots_and_call_graph(self):
        assert {f.path for f in self.inventory.files} == {"Bots/Main", "Bots/ConsultaPortal"}
        assert self.inventory.entrypoints == ["Bots/Main"]
        assert self.inventory.call_graph[0].target.endswith("Bots/ConsultaPortal")

    def test_ui_interactions_use_attribute_values(self):
        targets = [(u.tech, u.target) for u in self.inventory.ui_interactions]
        assert ("a360:Browser", "https://nfse.prefeitura.example/consulta") in targets
        assert ("a360:Recorder", "button#consultar") in targets

    def test_nested_nodes_keep_editor_line_order(self):
        http = self.inventory.http_calls[0]
        assert (http.file, http.line, http.method) == ("Bots/Main", 4, "GET")

    def test_data_sources_mask_secrets(self):
        kinds = {d.kind: d.ref for d in self.inventory.data_sources}
        assert "Pwd=***" in kinds["sqlserver"]
        assert "S3nh@Forte" not in self.inventory.to_json()
        assert kinds["excel"].endswith("pedidos.xlsx")

    def test_credentials_and_versioned_dependencies(self):
        assert self.inventory.credentials[0].ref == "PortalPrefeitura/senha"
        assert "a360:Database@3.1.0" in self.inventory.dependencies
        assert "a360:Database" not in self.inventory.dependencies

    def test_reads_bots_inside_zip(self, tmp_path):
        with zipfile.ZipFile(tmp_path / "export.zip", "w") as archive:
            for bot in (A360_PROJECT / "Bots").iterdir():
                archive.write(bot, f"Automation Anywhere/Bots/{bot.name}")
        inventory = A360Extractor().extract(tmp_path)
        assert inventory.entrypoints == ["export.zip!/Automation Anywhere/Bots/Main"]


class TestPython:
    inventory = PythonExtractor().extract(PYTHON_PROJECT)

    def test_entrypoint_and_local_imports(self):
        assert self.inventory.entrypoints == ["main.py"]
        edges = {(e.source, e.target) for e in self.inventory.call_graph}
        assert edges == {("main.py", "portal.py"), ("main.py", "db.py")}

    def test_ui_interactions(self):
        actions = {(u.line, u.action) for u in self.inventory.ui_interactions}
        assert (14, "find_element.click") in actions
        assert all(u.tech == "selenium" for u in self.inventory.ui_interactions)

    def test_http_calls_are_not_ui(self):
        assert [(h.method, h.url) for h in self.inventory.http_calls] == [
            ("POST", "https://hooks.example/notify")
        ]
        assert all(u.line != 16 for u in self.inventory.ui_interactions)

    def test_data_sources_and_secrets(self):
        kinds = [d.kind for d in self.inventory.data_sources]
        assert "sqlserver" in kinds and "excel" in kinds
        assert "S3nh@Forte" not in self.inventory.to_json()
        assert "abc123" not in self.inventory.to_json()

    def test_credentials(self):
        refs = {c.ref for c in self.inventory.credentials}
        assert refs == {"env:PORTAL_USER", "api_token (valor hardcoded)"}

    def test_dependencies_prefer_declared_versions(self):
        assert "selenium==4.21.0" in self.inventory.dependencies
        assert "selenium" not in self.inventory.dependencies


class TestDotNet:
    inventory = DotNetExtractor().extract(DOTNET_PROJECT)

    def test_ignores_build_output(self):
        assert not any(f.path.startswith("EmissaoBoleto/bin/") for f in self.inventory.files)

    def test_entrypoint_and_references(self):
        assert self.inventory.entrypoints == ["EmissaoBoleto/Program.cs"]
        edges = {(e.source, e.target) for e in self.inventory.call_graph}
        assert ("EmissaoBoleto/EmissaoBoleto.csproj", "Common/Common.vbproj") in edges
        assert ("EmissaoBoleto/Program.cs", "C:\\tools\\assinador.exe") in edges

    def test_selenium_interactions(self):
        actions = {(u.line, u.action, u.target) for u in self.inventory.ui_interactions}
        assert (22, "Navigate.GoToUrl", "https://banco.example/boletos") in actions
        assert (24, "FindElement.Click", "button#emitir") in actions
        assert all(u.line != 20 for u in self.inventory.ui_interactions)  # comentário

    def test_vb_win32_and_sendkeys(self):
        vb = {
            (u.line, u.tech) for u in self.inventory.ui_interactions if u.file == "Common/Janela.vb"
        }
        assert vb == {(11, "win32"), (12, "winforms")}  # a declaração P/Invoke não conta

    def test_http_calls_are_not_ui(self):
        assert [(h.line, h.method, h.lib) for h in self.inventory.http_calls] == [
            (25, "POST", "HttpClient")
        ]

    def test_data_sources_and_secrets(self):
        kinds = {(d.file, d.kind) for d in self.inventory.data_sources}
        assert ("Common/Janela.vb", "sqlserver") in kinds
        assert ("EmissaoBoleto/Program.cs", "excel") in kinds
        text = self.inventory.to_json()
        assert "S3nh@Forte" not in text and "x9y8z7" not in text and "abc123" not in text

    def test_credentials(self):
        refs = {c.ref for c in self.inventory.credentials}
        assert refs == {"env:PORTAL_USER", "config:PortalPassword", "ApiToken (valor hardcoded)"}

    def test_dependencies(self):
        deps = self.inventory.dependencies
        assert "Selenium.WebDriver@4.21.0" in deps and "Interop.SAPFEWSELib" in deps
        assert not any(d.startswith("System") for d in deps)


def test_cli_extracts_all_projects(tmp_path):
    input_dir = tmp_path / "input"
    shutil.copytree(A360_PROJECT, input_dir / "conciliacao-nf")
    shutil.copytree(PYTHON_PROJECT, input_dir / "consulta-portal")

    code = main(["extract", "--all", "--input", str(input_dir), "--output", str(tmp_path / "out")])

    assert code == 0
    for name, source in [("conciliacao-nf", "a360"), ("consulta-portal", "python")]:
        data = json.loads((tmp_path / "out" / name / "01-inventory/inventory.json").read_text())
        assert data["source_type"] == source


class TestPythonObjectOrigins:
    inventory = PythonExtractor().extract(FIXTURES / "python" / "scraping")

    def test_dict_get_is_not_ui(self):
        assert all(u.line != 6 for u in self.inventory.ui_interactions)

    def test_session_calls_are_http(self):
        assert [(h.line, h.method) for h in self.inventory.http_calls] == [(8, "GET")]
        assert all(u.line != 8 for u in self.inventory.ui_interactions)

    def test_html_scraping_is_recorded(self):
        assert {u.tech for u in self.inventory.ui_interactions if u.line in (9, 10)} == {"bs4"}

    def test_unknown_receiver_falls_back_to_imported_ui_lib(self):
        assert {u.tech for u in self.inventory.ui_interactions if u.line == 13} == {"selenium"}
