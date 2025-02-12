import concurrent.futures
import os

import requests
from bs4 import BeautifulSoup
from lxml import etree
from ics import Calendar

from utils import *
from datetime import datetime


# Get the HTML content of the website
base_url = "https://conf.researchr.org/"
response = requests.get(base_url)


# Get all the <h3> elements that contain the conference names and links
soup = BeautifulSoup(response.text, "lxml")
dom = etree.HTML(str(soup))
conferences = dom.xpath("//div[div[@class='panel-title' and text()='Upcoming Conferences']]/..//h3")


# Extract the events from the conferences
def fetch_conference_events(conference):
    events = []
    conference_name = conference.find("a").text
    conference_schedule_link = conference.find("a").get("href").replace("home", "dates")

    if conference_schedule_link.startswith(base_url):
        response = requests.get(conference_schedule_link)
        soup = BeautifulSoup(response.text, "lxml")
        dom = etree.HTML(str(soup))

        tr_elements = dom.xpath("//tr[@class='clickable-row text-success']")
        for tr in tr_elements:
            td_elements = tr.xpath(".//td")
            event_date = extract_row_element_text(td_elements[0])
            event_track = extract_row_element_text(td_elements[1])
            event_content = extract_row_element_text(td_elements[2])

            events.append({
                "conference": conference_name.strip(),
                "date": event_date.strip(),
                "track": event_track.strip(),
                "content": event_content.strip()
            })
    return events

events = []
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(fetch_conference_events, conference) for conference in conferences]
    for future in concurrent.futures.as_completed(futures):
        events.extend(future.result())

# Update the filter.json file with the new events
update_filter(events)

# Sort events by date, conference, track, and content
events = sorted(events, key=lambda x: (x["date"], x["conference"], x["track"], x["content"]))

# Compare events with the old events
if os.path.exists("results/conference_events.jsonl"):
    with open("results/conference_events.jsonl", "r") as f:
        old_events = [json.loads(line) for line in f.readlines()]

        if old_events == events:
            print("No new events found")
            exit()

# Save the new events to a file
os.makedirs("results", exist_ok=True)
with open("results/conference_events.jsonl", "w") as f:
    for event in events:
        f.write(json.dumps(event) + "\n")

# Create the events in the calendar
calendar = Calendar()
for event in events:
    event_conference = event["conference"]
    event_date = event["date"]
    event_track = event["track"]
    event_content = event["content"]

    if check_filter(event_conference, event_date, event_track, event_content):
        event = create_event(event_conference, event_date, event_track, event_content)
        calendar.events.add(event)

# Save the conference events to a file
with open(f"results/conference_events.ics", "w") as f:
    f.writelines(calendar)

# Upload the calendar to Google Calendar
upload_calendar_to_google(calendar.events)