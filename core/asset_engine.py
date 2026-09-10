import json
from pathlib import Path

ASSETS_FILE = Path("kiemaen_assets.json")

class AssetEngine:
    @staticmethod
    def register_asset(name: str, path_or_url: str):
        assets = AssetEngine.load_assets()
        clean_name = name.replace(":", "").strip()
        assets[clean_name] = path_or_url.strip()
        ASSETS_FILE.write_text(json.dumps(assets, indent=4), encoding="utf-8")
        return f"Asset '{clean_name}' registered successfully."

    @staticmethod
    def get_asset(name: str):
        assets = AssetEngine.load_assets()
        clean_name = name.replace(":", "").strip().lower()
        matches = {k: v for k, v in assets.items() if clean_name in k.lower()}
        return matches

    @staticmethod
    def load_assets():
        if ASSETS_FILE.exists():
            try:
                return json.loads(ASSETS_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}
