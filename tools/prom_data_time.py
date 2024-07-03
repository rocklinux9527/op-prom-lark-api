from datetime import datetime, timedelta

def add_hours_to_iso8601(iso8601_str, hours):
    if 'Z' in iso8601_str:
        iso8601_str_no_tz = iso8601_str.replace('Z', '')
    elif '+' in iso8601_str:
        iso8601_str_no_tz = iso8601_str.split('+')[0]
    elif '-' in iso8601_str:
        iso8601_str_no_tz = iso8601_str.split('-')[0]
    new_dt = iso8601_str_no_tz.split('.')[0]
    dt = datetime.fromisoformat(new_dt)
    return (dt + timedelta(hours=hours)).isoformat()
