import json
import sqlite3
from datetime import datetime
from typing import Union

from loguru import logger
import os

from source.common import time_converter_from_iso

db_path = os.path.join(os.getcwd(), "db_files", "trainings.db")


class DataBaseEditor:
    def __init__(self, path=None):
        if path is None:
            path = db_path
        logger.info("Initializing database.")
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER,
            start_date TEXT,
            sport_type TEXT,
            average_heartrate REAL,
            average_speed REAL,
            json_data TEXT
            )
        """)
        self.conn.commit()

    def check_if_data_exist(self, activity_id: int) -> bool:
        """
        Checks if a record with the given activity ID exists in the 'trainings' table.
        Args:
            activity_id (int): The ID of the activity to check.
        Returns:
            bool: True if the record exists, False otherwise.
        """
        try:
            self.cursor.execute("SELECT 1 FROM trainings WHERE activity_id = ?", (activity_id,))
            is_exists = bool(self.cursor.fetchone())
            if is_exists:
                logger.info(f"Activity with id {activity_id} already exists in database. Fetching skipped.")
            return is_exists
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                logger.error("The 'trainings' table does not exist.")
                return False
            else:
                raise

    def add_activity_to_db(self, activity, data) -> bool:
        """
        Inserts a new activity record into the 'trainings' table in the database.

        Parameters:
            activity (dict): A dictionary containing basic activity data.
                             Expected keys: 'id', 'sport_type', 'average_heartrate', 'average_speed'.
            data (dict): Additional activity data to be stored as JSON in the 'json_data' column.

        Commits the transaction after insertion. Logs a success message if the insert was successful,
        otherwise logs a warning.

        Returns:
            bool: True if the activity was successfully inserted into the database,
                  False if the insertion failed.
        """
        try:
            self.cursor.execute(
                "INSERT INTO trainings "
                "(activity_id, "
                "start_date, "
                "sport_type, "
                "average_heartrate, "
                "average_speed, json_data) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    activity["id"],
                    time_converter_from_iso(activity["start_date"]),
                    activity["sport_type"],
                    activity["average_heartrate"],
                    activity["average_speed"],
                    json.dumps(data),
                ),
            )
            self.conn.commit()
            if self.cursor.lastrowid is not None:
                logger.success("Successfully added activity to database.")
                return True
            else:
                logger.warning("Activity not added to database.")
                return False
        except KeyError as e:
            logger.warning("Failed to add activity to database.", e)
            return False

    def clear_whole_database(self) -> bool:
        """
        Prompts the user for confirmation and deletes the entire 'trainings' table from the database if confirmed.

        This action is irreversible and will permanently remove all data from the 'trainings' table.
        Asks the user to confirm by typing 'y'. Logs a warning before deletion and logs success after completion.

        Returns:
        bool: True if the table was deleted, False if the deletion was cancelled.
        """
        logger.warning("Deleting database.")
        decision = input("Would you like to delete all records? (y/n) ")
        if decision == "y":
            self.cursor.execute("DROP TABLE IF EXISTS trainings")
            self.conn.commit()
            logger.success("Successfully deleted all records.")
            return True
        else:
            logger.warning("Deletion aborted.")
            return False

    @staticmethod
    def _prepare_dates(start_date, end_date):
        if start_date == end_date:
            logger.info("Please enter dates with at least two days in range.")
            return []
        return [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]

    def read_data_in_time_range(self, start_date: str, end_date: str) -> Union[list, None]:
        """
        Retrieves all training records from the database that fall within the specified date range.

        Args:
            start_date (str): The start date in the format 'YYYY-MM-DD'.
            end_date (str): The end date in the format 'YYYY-MM-DD'.

        Returns:
            list: A list of tuples, each representing a training record within the given time range.
        """

        try:
            start_date, end_date = self._prepare_dates(start_date, end_date)
            datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            self.cursor.execute("SELECT * FROM trainings WHERE start_date BETWEEN ? AND ?", (start_date, end_date))
            data = self.cursor.fetchall()
            if data:
                return data
            else:
                logger.info("Thera are no records within the time range.")
                return []
        except ValueError:
            logger.error("Invalid start and/or end date.")
            return []

    def read_data_in_hr_range(
        self, start_date: str, end_date: str, min_hr: Union[int, float] = 60, max_hr: Union[int, float] = 210
    ) -> Union[list, None]:
        start_date, end_date = self._prepare_dates(start_date, end_date)
        try:
            datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "SELECT * FROM trainings WHERE start_date BETWEEN ? AND ? "
                "AND average_heartrate BETWEEN ? AND ? ORDER BY start_date",
                (start_date, end_date, min_hr, max_hr),
            )
            data = self.cursor.fetchall()
            if data:
                return data
            else:
                logger.info("Thera are no records within the time range.")
                return []
        except ValueError:
            logger.error("Invalid start and/or end date.")
            return []
