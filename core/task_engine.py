import json
from pathlib import Path

TASKS_FILE = Path("kiemaen_tasks.json")

class TaskEngine:
    @staticmethod
    def add_task(task_description: str):
        tasks = TaskEngine.load_tasks()
        clean_task = task_description.replace("add task", "").strip()
        tasks.append({"task": clean_task, "status": "pending"})
        TASKS_FILE.write_text(json.dumps(tasks, indent=4), encoding="utf-8")
        return f"Task added: '{clean_task}'"

    @staticmethod
    def get_tasks():
        tasks = TaskEngine.load_tasks()
        if not tasks:
            return "No active tasks found."
        formatted = "<br>".join([f"- {t['task']} [{t['status']}]" for t in tasks])
        return f"Your Tasks:<br>{formatted}"

    @staticmethod
    def load_tasks():
        if TASKS_FILE.exists():
            try:
                return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []
