
from datetime import datetime, timedelta
import pytz
from dateutil import parser as dateparser
from dateparser import parse as date_parse
from datetime import datetime
import pytz

def to_rfc3339(time_str, default_date=None, timezone_str="Asia/Kolkata"):
    tz = pytz.timezone(timezone_str)
    now = datetime.now(tz)

    if default_date is None:
        default_date = now.strftime("%Y-%m-%d")

    try:
        # Try parsing the time_str as-is first
        dt = date_parse(time_str, settings={'PREFER_DATES_FROM': 'current_period'})

        # If parsing fails, prepend default_date and try again
        if dt is None:
            time_str = f"{default_date} {time_str}"
            dt = date_parse(time_str, settings={'PREFER_DATES_FROM': 'current_period'})

        if dt is None:
            raise ValueError(f"Could not parse datetime from '{time_str}'")

        # Localize to the specified timezone if naive
        if dt.tzinfo is None:
            dt = tz.localize(dt)

        return dt.isoformat()

    except Exception as e:
        raise ValueError(f"Invalid time format: '{time_str}' → {e}")



# def to_rfc3339(time_str, default_date=None, timezone_str="Asia/Kolkata"):
#     tz = pytz.timezone(timezone_str)
#     now = datetime.now(tz)

#     # Add a default date if the time_str doesn't contain one
#     if default_date is None:
#         default_date = now.strftime("%Y-%m-%d")

#     try:
#         # Combine default date + time string if needed
#         if "T" not in time_str and ":" in time_str:
#             time_str = f"{default_date} {time_str}"

#         dt = dateparser.parse(time_str)
#         if dt.tzinfo is None:
#             dt = tz.localize(dt)
#         return dt.isoformat()
#     except Exception as e:
#         raise ValueError(f"Invalid time format: '{time_str}' → {e}")

