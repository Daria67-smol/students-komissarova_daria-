import functools
from datetime import datetime
from pathlib import Path

def log_action(log_path: Path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            func_name = func.__name__

            log_entry = f"[{timestamp}] {func_name} args={args[1:]} kwargs={kwargs}"
            try:
                result = func(*args, **kwargs)
                log_entry += " status=SUCCESS\n"
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                return result
            except Exception as e:
                log_entry += f" status=ERROR: {e}\n"
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                raise
        return wrapper
    return decorator
