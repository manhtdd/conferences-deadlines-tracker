import concurrent.futures
import json

import requests
from bs4 import BeautifulSoup
from lxml import etree
from ics import Calendar

from helper import *


# Get the HTML content of the website
base_url = "https://conf.researchr.org/"
response = requests.get(base_url)


# Get all the <h3> elements that contain the conference names and links
soup = BeautifulSoup(response.text, "lxml")
dom = etree.HTML(str(soup))
conferences = dom.xpath("//div[div[@class='panel-title' and text()='Upcoming Conferences']]/..//h3")


# Extract the events from the conferences
calendar = Calendar()

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
            event_title = extract_row_element_text(td_elements[2])

            event = create_event(conference_name, event_date, event_track, event_title)
            events.append(event)
    return events

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(fetch_conference_events, conference) for conference in conferences]
    for future in concurrent.futures.as_completed(futures):
        calendar.events.update(future.result())

# Save the conference events to a file
with open("conference_events.ics", "w") as f:
    f.writelines(calendar)