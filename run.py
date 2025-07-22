import uvicorn
from main import create_app
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
