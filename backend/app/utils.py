
from datetime import datetime, timedelta
import pytz
from dateutil import parser as dateparser

def to_rfc3339(time_str, default_date=None, timezone_str="Asia/Kolkata"):
    tz = pytz.timezone(timezone_str)
    now = datetime.now(tz)

    # Add a default date if the time_str doesn't contain one
    if default_date is None:
        default_date = now.strftime("%Y-%m-%d")

    try:
        # Combine default date + time string if needed
        if "T" not in time_str and ":" in time_str:
            time_str = f"{default_date} {time_str}"

        dt = dateparser.parse(time_str)
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        return dt.isoformat()
    except Exception as e:
        raise ValueError(f"Invalid time format: '{time_str}' → {e}")

