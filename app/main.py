import os
import sys
import importlib.util

# Load backend/app/main.py directly by file path to avoid circular import
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

_spec = importlib.util.spec_from_file_location(
    "backend_main",
    os.path.join(_backend_dir, "app", "main.py")
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["backend_main"] = _mod
_spec.loader.exec_module(_mod)

app = _mod.app
