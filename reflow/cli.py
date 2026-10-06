import argparse
import sys
from pathlib import Path

from reflow.extractors import find_extractor

INVENTORY_FILE = "01-inventory/inventory.json"


def extract_project(project_dir: Path, output_dir: Path) -> Path:
    extractor = find_extractor(project_dir)
    inventory = extractor.extract(project_dir)
    target = output_dir / project_dir.name / INVENTORY_FILE
    inventory.save(target)
    return target


def _projects(input_dir: Path, name: str | None) -> list[Path]:
    if name:
        project = input_dir / name
        if not project.is_dir():
            raise SystemExit(f"Projeto não encontrado: {project}")
        return [project]
    return sorted(p for p in input_dir.iterdir() if p.is_dir() and not p.name.startswith("."))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="reflow", description="Extração determinística do reflow")
    sub = parser.add_subparsers(dest="command", required=True)
    extract = sub.add_parser("extract", help="gera output/<projeto>/01-inventory/inventory.json")
    target = extract.add_mutually_exclusive_group(required=True)
    target.add_argument("project", nargs="?", help="nome da subpasta em input/")
    target.add_argument("--all", action="store_true", help="todos os projetos de input/")
    extract.add_argument("--input", type=Path, default=Path("input"))
    extract.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args(argv)

    failures = 0
    for project in _projects(args.input, None if args.all else args.project):
        try:
            print(f"{project.name}: {extract_project(project, args.output)}")
        except ValueError as error:
            failures += 1
            print(f"{project.name}: ERRO {error}", file=sys.stderr)
    return 1 if failures else 0
