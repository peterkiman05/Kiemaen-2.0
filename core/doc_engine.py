import json
from pathlib import Path

NOTES_FILE = Path("kiemaen_notes.json")


class DocumentEngine:
    @staticmethod
    def save_note(title: str, content: str):
        notes = DocumentEngine.load_notes()
        clean_title = title.replace(":", "").strip()
        notes[clean_title] = content.strip()
        NOTES_FILE.write_text(json.dumps(notes, indent=4), encoding="utf-8")
        return f"Note '{clean_title}' saved successfully."

    @staticmethod
    def search_notes(keyword: str):
        notes = DocumentEngine.load_notes()
        clean_keyword = keyword.replace(":", "").strip().lower()
        results = {
            t: c
            for t, c in notes.items()
            if clean_keyword in t.lower() or clean_keyword in c.lower()
        }
        return results

    @staticmethod
    def load_notes():
        if NOTES_FILE.exists():
            try:
                return json.loads(NOTES_FILE.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}
