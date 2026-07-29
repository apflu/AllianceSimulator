import ast
from pathlib import Path


def test_domain_does_not_import_frameworks() -> None:
    banned = ("aiogram", "discord", "fastapi", "sqlalchemy")
    domain_root = Path("src/alliancesim/domain")
    violations: list[str] = []
    for path in domain_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            for name in names:
                if name.startswith(banned):
                    violations.append(f"{path}: {name}")
    assert not violations, "domain framework imports: " + ", ".join(violations)
