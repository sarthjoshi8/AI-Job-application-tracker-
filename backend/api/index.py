import sys
import os
from pathlib import Path

# Vercel runs this file from /var/task/api/index.py
# The 'backend' directory (parent of 'api') must be on sys.path
# so that `from app.xxx import yyy` works correctly.
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Also change working directory to backend root
os.chdir(str(backend_dir))

from app.main import app
