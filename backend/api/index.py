import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
app_dir = root_dir / "app"

for p in [str(root_dir), str(app_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.main import app
