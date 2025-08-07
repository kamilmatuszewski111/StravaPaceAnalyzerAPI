import json
import sqlite3
from loguru import logger
import os

db_path = os.path.join(os.getcwd(), "db_files", "trainings.db")

class DataBaseEditor:
    def __init__(self):
        logger.info("Initializing database.")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER,
            sport_type TEXT,
            average_heartrate REAL,
            average_speed REAL,
            json_data TEXT
            )
        ''')
        self.conn.commit()

    def check_if_data_exist(self, activity_id: int) -> bool:
        """
           Checks if a record with the given activity ID exists in the 'trainings' table.
           Args:
               activity_id (int): The ID of the activity to check.
           Returns:
               bool: True if the record exists, False otherwise.
           """
        self.cursor.execute("SELECT 1 FROM trainings WHERE activity_id = ?", (activity_id,))
        is_exists = bool(self.cursor.fetchone())
        logger.info(f"Activity with id {activity_id} already exists in the 'trainings' database. Fetching skipped.") \
            if is_exists else None
        return is_exists


    def add_activity_to_db(self, activity, data):
        """
        Inserts a new activity record into the 'trainings' table in the database.

        Parameters:
            activity (dict): A dictionary containing basic activity data.
                             Expected keys: 'id', 'sport_type', 'average_heartrate', 'average_speed'.
            data (dict): Additional activity data to be stored as JSON in the 'json_data' column.

        Commits the transaction after insertion. Logs a success message if the insert was successful,
        otherwise logs a warning.
        """
        self.cursor.execute("INSERT INTO trainings "
                            "(activity_id, "
                            "sport_type, "
                            "average_heartrate, "
                            "average_speed, json_data) VALUES (?, ?, ?, ?, ?)",
                            (activity['id'], activity['sport_type'],
                             activity['average_heartrate'], activity['average_speed'], json.dumps(data)))
        self.conn.commit()
        logger.success("Successfully added activity to database.") if self.cursor.lastrowid is not None else (
            logger.warning("Activity not added to database."))


    def clear_whole_database(self):
        """
        Prompts the user for confirmation and deletes the entire 'trainings' table from the database if confirmed.

        This action is irreversible and will permanently remove all data from the 'trainings' table.
        Asks the user to confirm by typing 'y'. Logs a warning before deletion and logs success after completion.
        """
        logger.warning("Deleting database.")
        decision = input("Would you like to delete all records? (y/n) ")
        if decision == "y":
            self.cursor.execute("DROP TABLE IF EXISTS trainings")
            self.conn.commit()
            logger.success("Successfully deleted all records.")