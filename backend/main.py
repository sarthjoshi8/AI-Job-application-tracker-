import sys
from pathlib import Path

# Ensure the backend directory is in the python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import app
