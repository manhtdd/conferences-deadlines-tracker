import re

from ics import Event
from datetime import datetime, timezone, timedelta

MONTH_DICT = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}
AOE_TZ = timezone(timedelta(hours=-12))

def extract_row_element_text(td):
    if td.text:
        return td.text
    else:
        return td.find("strong").text
    
def get_date(event_date):
    # Find Hour::Minute
    hour_minute = re.search(r"\d{1,2}:\d{1,2}", event_date)
    if hour_minute:
        hour_minute = hour_minute.group()
        event_date = event_date.replace(hour_minute, "")
    
    hour = int(hour_minute.split(":")[0]) if hour_minute else None
    minute = int(hour_minute.split(":")[1]) if hour_minute else None

    # Find year
    year = re.search(r"\d{4}", event_date)
    if year:
        year = year.group()
        event_date = event_date.replace(year, "")

    # Find month
    month = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", event_date)
    if month:
        month = month.group()
        event_date = event_date.replace(month, "")

    # Find day
    day = re.search(r"\d{1,2}", event_date)
    if day:
        day = day.group()
        event_date = event_date.replace(day, "")

    return year, month, day, hour, minute
    
def create_event(event_conference, event_date, event_track, event_title):
    event = Event()
    
    event.name = event_conference + " - " + event_title
    event.description = f"""
        Conference: {event_conference}
        Date: {event_date}
        Track: {event_track}
    """
    event_date = event_date.strip()

    # Only 1 day event:
    if '-' not in event_date:
        year, month, day, _, _ = get_date(event_date)
        event.begin = datetime(int(year), MONTH_DICT[month], int(day), 0, 0).replace(tzinfo=AOE_TZ)
        event.end = (datetime(int(year), MONTH_DICT[month], int(day), 23, 59) + timedelta(minutes=1)).replace(tzinfo=AOE_TZ)

        return event
    else:
        start_date, end_date = event_date.split("-")

        # Get year, month, day, hour and minute
        start_year, start_month, start_day, start_hour, start_minute = get_date(start_date)
        end_year, end_month, end_day, end_hour, end_minute = get_date(end_date)

        # If start year, month and day are None, set them to end year, month and day and vice versa
        start_year = start_year if start_year else end_year
        end_year = end_year if end_year else start_year

        start_month = start_month if start_month else end_month
        end_month = end_month if end_month else start_month

        start_day = start_day if start_day else end_day
        end_day = end_day if end_day else start_day

        # Set default values if they are None
        start_hour = 0 if start_hour is None else start_hour
        start_minute = 0 if start_minute is None else start_minute
        end_hour = 23 if end_hour is None else end_hour
        end_minute = 59 if end_minute is None else end_minute

        event.begin = datetime(int(start_year), MONTH_DICT[start_month], int(start_day), start_hour, start_minute).replace(tzinfo=AOE_TZ)
        event.end = (datetime(int(end_year), MONTH_DICT[end_month], int(end_day), end_hour, end_minute) + timedelta(minutes=1)).replace(tzinfo=AOE_TZ)

        return event