import io
import sys
import math
import json
import traceback
from concurrent.futures import ProcessPoolExecutor, TimeoutError

def _worker_exec(code_string: str):
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    try:
        cleaned = code_string.replace("```python", "").replace("```", "").strip()
        if cleaned.lower().startswith("run"):
            cleaned = cleaned[3:].strip()

        safe_globals = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bool": bool,
                "dict": dict, "enumerate": enumerate, "float": float,
                "int": int, "len": len, "list": list, "map": map,
                "max": max, "min": min, "print": print, "range": range,
                "set": set, "str": str, "sum": sum, "tuple": tuple,
                "zip": zip,
            },
            "math": math,
            "json": json,
        }

        exec(cleaned, safe_globals)
        output = redirected_output.getvalue()
        status = "success"
    except Exception:
        output = traceback.format_exc()
        status = "error"
    finally:
        sys.stdout = old_stdout

    return status, output if output else "Executed successfully with no output."

def execute_python(code_string: str, timeout_seconds: int = 5):
    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_worker_exec, code_string)
        try:
            status, output = future.result(timeout=timeout_seconds)
        except TimeoutError:
            status = "timeout_error"
            output = f"Execution timed out ({timeout_seconds}s limit reached)."
        except Exception as e:
            status = "error"
            output = str(e)

    return {
        "status": status,
        "output": output
    }
