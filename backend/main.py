import sys
from pathlib import Path

# Add backend directory to sys.path so app modules are discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import app
