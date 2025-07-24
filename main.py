import time

from token_manager import TokenManager
from api import StravaAPI
from loguru import logger

def main():
    token_manager = TokenManager()
    api = StravaAPI(token_manager)

    logger.info("Create datetime params. Please put your start and end date.")
    time.sleep(0.5)
    start_date = input("Start date in YYYY-MM-DD format")
    end_date = input("End date in YYYY-MM-DD format")

    activities = api.get_activities(start_date, end_date)
    if not activities:
        print("No activities found.")
        return

    for act in activities:
        print(f"{act['name']} | {act['start_date_local']} | {act['distance'] / 1000:.2f} km")
        stream = api.get_activity_streams(act["id"])

if __name__ == "__main__":
    main()


