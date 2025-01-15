from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from django.utils.dateparse import parse_datetime, parse_date
from django.utils.timezone import make_aware, is_aware


def to_filename(dt: Optional[datetime]) -> str:
    if dt is None:
        return ""
    return dt.strftime("%Y-%m%d-%H-00")

def to_datetime_tz_aware(value: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    naive_date = datetime.strptime(value, format)
    aware_date = naive_date.replace(tzinfo=ZoneInfo("UTC"))

    return aware_date

def parse_flexible_date(date_string: Optional[str]) -> Optional[datetime]:
    """
    Parses a string datetime or date without time.
    Raises:
        ValueError: If the date_string cannot be parsed as either date or datetime    
    """
    if not date_string:
        return None
    
    input_date = parse_datetime(date_string)
    if input_date:
        return make_aware(input_date) if not is_aware(input_date) else input_date
    
    input_date = parse_date(date_string)
    if input_date:
        return make_aware(datetime.combine(input_date, datetime.min.time()))
        
    raise ValueError(f"Invalid date format: {date_string}")