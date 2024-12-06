from datetime import datetime

def datetime_to_filename(dt: datetime|None) -> str:
    if dt is None:
        return ""
    return dt.strftime("%Y-%m%d-%H-00")