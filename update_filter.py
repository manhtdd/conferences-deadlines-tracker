import json, re, os

def read_conference_events(file_path):
    events = []
    with open(file_path, 'r') as file:
        for line in file:
            events.append(json.loads(line))
    return events

file_path = './conference_events.jsonl'
events = read_conference_events(file_path)

try:
    with open('filter.json', 'r') as filter_file:
        filters = json.load(filter_file)
except Exception as e:
    filters = {}

# Filter Conferences
if 'conference_filter' not in filters:
    filters['conference_filter'] = {}

current_conferences = set()

for event in events:
    conference_name = re.sub(r'\b-?\d{4}\b', '', event['conference']).strip()
    current_conferences.add(conference_name)

for conference in current_conferences:
    if conference not in filters['conference_filter']:
        filters['conference_filter'][conference] = False
filters['conference_filter'] = {k: v for k, v in sorted(filters['conference_filter'].items())}

# Filter Tracks
if 'track_filter' not in filters:
    filters['track_filter'] = {}

for conference in filters['conference_filter']:
    if conference not in filters['track_filter']:
        filters['track_filter'][conference] = {}
    
    tracks = set()
    for event in events:
        if event['conference'].startswith(conference):
            tracks.add(event['track'])

    for track in tracks:
        if track not in filters['track_filter'][conference]:
            filters['track_filter'][conference][track] = False
    filters['track_filter'][conference] = {k: v for k, v in sorted(filters['track_filter'][conference].items())}

# Filter Contents
if 'content_filter' not in filters:
    filters['content_filter'] = {}

for event in events:
    content = event['content']
    if content not in filters['content_filter']:
        filters['content_filter'][content] = False
filters['content_filter'] = {k: v for k, v in sorted(filters['content_filter'].items())}

# Export the filters
with open('filter.json', 'w') as filter_file:
    json.dump(filters, filter_file, indent=4)