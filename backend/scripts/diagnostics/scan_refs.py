"""Search for references to specific symbols/imports across the codebase."""
import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
APP = ROOT / "app"

TARGETS = [
    "app.services.address",
    "app.schemas.addresses",
    "app.crud.address",
    "AddressService",
    "get_current_customer",
    "get_current_technician",
    "CustomerAddressCreate",
    "CustomerAddressUpdate",
    "CustomerAddressResponse",
    "config",
]

for file in sorted(APP.rglob("*.py")):
    try:
        text = file.read_text(encoding="utf-8")
    except Exception:
        continue
    rel = file.relative_to(ROOT)
    for target in TARGETS:
        if target in text:
            print(f"{rel}: references '{target}'")

