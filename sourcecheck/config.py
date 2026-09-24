"""Local runtime configuration with no sibling-repository dependencies."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.getenv("SOURCECHECK_DATA", str(ROOT / ".runtime"))).resolve()
TOOLS = Path(os.getenv("SOURCECHECK_TOOLS", str(ROOT / "external" / "tools"))).resolve()
MODELS = Path(os.getenv("SOURCECHECK_MODELS", str(DATA / "models"))).resolve()
MAX_FILE = 25 * 1024 * 1024
MAX_PAGES = 20
MAX_PIXELS = 18_000_000
VERSIONS = ("2.26.0", "2.24.0")
