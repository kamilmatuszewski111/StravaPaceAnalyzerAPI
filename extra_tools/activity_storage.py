import json
import os
from datetime import datetime

DATA_FILE = "activities_data.json"

def load_existing_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    sorted_data = dict(sorted(
        data.items(),
        key=lambda item: item[1]["date"]
    ))
    with open(DATA_FILE, "w") as f:
        json.dump(sorted_data, f, indent=2)



def process_activity(activity_id, activity_data, data_store):
    if str(activity_id) in data_store:
        print(f"Pomijam {activity_id} – już w pliku.")
        return

    # Przykład danych – dostosuj do tego co pobierasz z API
    data_store[str(activity_id)] = {
        "date": activity_data["start_date_local"],
        "heartrate": activity_data.get("heartrate_stream", []),
        "watts": activity_data.get("watts_stream", [])
    }