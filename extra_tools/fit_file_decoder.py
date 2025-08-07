import os
from loguru import logger
from garmin_fit_sdk import Decoder, Stream
from collections import defaultdict
from datetime import timedelta


class FitFileDecoder:
    """
    A class for decoding FIT files and extracting workout data.
    """
    def __init__(self, file_path):
        """
        Initializes the FIT file decoder.

        :param file_path: Path to the FIT file.
        """
        self.file_path = file_path
        self.messages = None
        self.expected_data = []
        self.dict_items = defaultdict(list)
        self.low_hr_limit = 0
        self.high_hr_limit = 210
        self.training_date = None

    def define_records(self, *args):
        """
        Defines the list of records to extract from the FIT file.

        :param args: Data keys to be extracted (e.g., 'heart_rate', 'enhanced_speed').
        """
        self.expected_data = args

    def define_hr_limits(self, low_limit, high_limit):
        """
        Sets the heart rate range for filtering data.

        :param low_limit: Lower heart rate limit.
        :param high_limit: Upper heart rate limit.
        """
        logger.info("Defining Hear Rate limits")
        self.low_hr_limit = low_limit
        self.high_hr_limit = high_limit
        logger.success(f"Limits defined to {self.low_hr_limit} and {self.high_hr_limit}")

    def _read_fit_file(self):
        """
        Reads and decodes the FIT file.
        """
        if not os.path.exists(self.file_path):
            logger.error(f"File not found: {self.file_path}")
            raise FileNotFoundError(f"File not found: {self.file_path}")

        logger.info("Reading FIT file")
        stream = Stream.from_file(self.file_path)
        decoder = Decoder(stream)
        messages, errors = decoder.read()
        self.messages = messages

        if self.messages:
            logger.success("FIT file decoded successfully.")
        else:
            logger.error("FIT file does not decoded successfully.")

        if errors:
            logger.error(f"Errors while decoding FIT file: {errors}")
            raise ValueError(f"Failed to decode FIT file: {errors}")

    def _extract_data(self):
        """
        Extracts the specified data fields from the FIT file records.
        """
        for record in self.messages["record_mesgs"]:
            for data in self.expected_data:
                if data in record and record[data] is not None:
                    self.dict_items[data].append(record[data])

    @staticmethod
    def pace_calculate(speed):
        """
        Calculates the pace based on speed.

        :param speed: Speed in km/h.
        :return: Pace as a timedelta object.
        """
        pace_min_to_km = 60 / speed if speed > 0 else 0
        minutes = int(pace_min_to_km)
        seconds = round((pace_min_to_km - minutes) * 60)

        return timedelta(minutes=minutes, seconds=seconds)

    def execute_extracting(self):
        """
        Executes the process of reading and extracting data from the FIT file.
        """
        self._read_fit_file()
        self._extract_data()

        if "enhanced_speed" in self.expected_data:
            self.dict_items["pace"] = [self.pace_calculate(x*3.6) for x in self.dict_items["enhanced_speed"]]

    def pace_within_limit(self):
        """
        Filters pace values, keeping only those within the defined heart rate limits.

        :return: A list of pace values as timedelta objects.
        """
        temp_pace = []
        for pace, hr in zip(self.dict_items['pace'], self.dict_items['heart_rate']):
            if self.low_hr_limit <= hr <= self.high_hr_limit:
                temp_pace.append(pace)
        return temp_pace

    def calculate_average_pace(self):
        """
        Calculates the average pace for heart rate records within the defined limits.

        :return: The average pace as a timedelta object.
        """
        self.execute_extracting()
        valid_paces = self.pace_within_limit()

        if not valid_paces:
            logger.warning("No valid paces found within the heart rate limits.")
            return None

        average_pace = sum(valid_paces, timedelta()) / len(valid_paces)
        av_min = int(average_pace.total_seconds() // 60)
        av_sec = int(average_pace.total_seconds() % 60)

        self.training_date = self.messages["activity_mesgs"][0]['timestamp']
        formatted_date = self.training_date.strftime("%Y-%m-%d %H:%M:%S %Z")
        if av_min and av_sec:
            logger.success(f"Training date: {formatted_date}")
            logger.success(f"Average pace within {self.low_hr_limit} - {self.high_hr_limit} -> "
                           f"{av_min}:{round(av_sec, 2)}")
        return {self.training_date: average_pace}

