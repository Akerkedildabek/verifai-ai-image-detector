from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
required = [
    "app.py", "requirements.txt", ".streamlit/config.toml",
    "src/detector.py", "src/metadata.py", "src/i18n.py", "src/ui.py",
    "README.md", "DEPLOYMENT_KZ.md",
]
for item in required:
    p = ROOT / item
    assert p.exists(), f"Missing {item}"
for p in ROOT.rglob("*.py"):
    ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
print("PROJECT_STRUCTURE_OK")
