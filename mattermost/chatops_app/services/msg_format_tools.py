from datetime import datetime
from typing import Dict

TIMESTAMP_FMT = '%d %b %Y %H:%M'


def rename_and_format_dict(data: Dict, keys_rename: Dict[str, str]) -> Dict:
    formatted = {}
    for key, value in data.items():
        if key in keys_rename:
            if isinstance(value, datetime):
                value = value.strftime(TIMESTAMP_FMT)
            formatted[keys_rename[key]] = value or ''

    return formatted
