from django import template
from datetime import datetime
import pytz

register = template.Library()


@register.filter
def convert_utc_to_local(utc_dt, timezone_name):
    if not isinstance(utc_dt, datetime):
        return utc_dt

    local_tz = pytz.timezone(timezone_name)
    local_dt = utc_dt.astimezone(local_tz)
    return local_dt.strftime("%Y-%m-%d %H:%M")
