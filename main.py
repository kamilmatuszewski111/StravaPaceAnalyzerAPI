import time

from loguru import logger

from source.api import StravaAPI
from source.database import DataBaseEditor
from source.token_manager import TokenManager


def main():
    token_manager = TokenManager()
    api = StravaAPI(token_manager)
    db = DataBaseEditor()

    logger.info("Create datetime params. Please put your start and end date.")
    time.sleep(0.5)
    start_date = input("Start date in YYYY-MM-DD format")
    end_date = input("End date in YYYY-MM-DD format")

    activities = api.get_activities(start_date, end_date, "Run")
    if not activities:
        logger.warning("No activities found.")
        return

    for act in activities:
        logger.info(f"{act['id']} | {act['name']} | {act['start_date_local']} | {act['distance'] / 1000:.2f} km")
        if not db.check_if_data_exist(act['id']):
            stream = api.get_activity_streams(act["id"])
            db.add_activity_to_db(act, stream)


if __name__ == "__main__":
    main()