import os
import sys
from pathlib import Path

# Add backend directory and current directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure root directory is current working directory
os.chdir(str(BASE_DIR))

try:
    from app.main import app
except Exception as e:
    import traceback
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse

    app = FastAPI()

    @app.get("/{full_path:path}")
    async def debug_error(full_path: str):
        return PlainTextResponse(
            f"Error importing app:\n\n{traceback.format_exc()}\n\nPaths:\nsys.path={sys.path}\nos.listdir={os.listdir('.')}",
            status_code=500
        )
