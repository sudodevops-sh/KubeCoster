import re
from datetime import timedelta

def parse_duration(duration_str):
    """Converts strings like '24h' or '7d' into total seconds."""
    match = re.match(r"([0-9]+)([hd])", duration_str)
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")
    value, unit = match.groups()
    value = int(value)
    if unit == "h":
        return value * 3600
    elif unit == "d":
        return value * 86400
    else:
        return 0
        