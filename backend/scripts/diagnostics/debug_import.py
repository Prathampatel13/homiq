import importlib.util
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

spec = importlib.util.find_spec("app.main")
print(spec)
module = importlib.import_module("app.main")
print(module.app)
