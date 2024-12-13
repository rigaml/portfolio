from datetime import datetime
from zoneinfo import ZoneInfo

def to_filename(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.strftime("%Y-%m%d-%H-00")

def to_datetime_tz_aware(value: str, format:str = "%Y-%m-%d %H:%M:%S") -> datetime:
    naive_date = datetime.strptime(value, format)
    aware_date = naive_date.replace(tzinfo=ZoneInfo("UTC"))

    return aware_date