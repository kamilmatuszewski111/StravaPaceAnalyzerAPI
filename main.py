import time

from common import DataAnalyzer, Plot
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
        if not db.check_if_data_exist(act["id"]):
            stream = api.get_activity_streams(act["id"])
            db.add_activity_to_db(act, stream)

    data = db.read_data_in_hr_range(start_date, end_date, 60, 155)
    data_analyzer = DataAnalyzer(data)
    extracted_data = data_analyzer.extract_date_and_hr()

    times = [DataAnalyzer.mmss_to_minutes(data[1]) for data in extracted_data]
    dates = [data[0] for data in extracted_data]

    plt = Plot(dates, times)
    plt.show_plot()


if __name__ == "__main__":
    main()
