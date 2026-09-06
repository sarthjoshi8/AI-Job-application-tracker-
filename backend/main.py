import os
import sys
from pathlib import Path

# Add /var/task and backend directories to sys.path
root_dir = Path(__file__).resolve().parent
app_dir = root_dir / "app"

for p in [str(root_dir), str(app_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.main import app
