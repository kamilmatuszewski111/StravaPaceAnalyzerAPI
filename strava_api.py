import requests
import time
import json
from loguru import logger
from collections import defaultdict
import os
from dotenv import load_dotenv

TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
ONE_ACTIVITY_TEMPLATE = 'https://www.strava.com/api/v3/activities/{}/streams'



class StravaAPIRequests:
    def __init__(self):
        self.loaded_tokens = defaultdict()
        load_dotenv(override=True)
        self._load_tokens()
        self.start_date = None
        self.end_date = None
        self.activities = None


    def _save_to_env(self, data: dict):
        logger.info("Saving data to .env file.")
        with open(".env", "w") as file:
            for key, value in data.items():
                file.write(f"{key.upper()}={value}\n")

    def _load_tokens(self):
        logger.info("Loading tokens from env file.")
        # with open("api_tokens.json", "r", encoding="utf-8") as file:
        #     self.loaded_tokens = json.load(file)
        self.loaded_tokens["CLIENT_ID"] = int(os.getenv("CLIENT_ID"))
        self.loaded_tokens["CLIENT_SECRET"] = os.getenv("CLIENT_SECRET")
        self.loaded_tokens["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
        self.loaded_tokens["REFRESH_TOKEN"] = os.getenv("REFRESH_TOKEN")
        self.loaded_tokens["EXPIRES_AT"] = int(os.getenv("EXPIRES_AT"))
        return self.loaded_tokens

    @staticmethod
    def _is_token_expired(expires_at):
        return time.time() > expires_at

    def refresh_token(self):
        logger.info("Start refresh token.")
        loaded_tokens = self._load_tokens()
        response = requests.post(TOKEN_URL, data={
            "client_id": loaded_tokens["CLIENT_ID"],
            "client_secret": loaded_tokens["CLIENT_SECRET"],
            "refresh_token": loaded_tokens["REFRESH_TOKEN"],
            "grant_type": "refresh_token"
        })

        if response.status_code == 200:
            logger.success("Token refresh procedure performed successfully.")
            data = response.json()

            data["CLIENT_ID"] = self.loaded_tokens["CLIENT_ID"]
            data["CLIENT_SECRET"] = self.loaded_tokens["CLIENT_SECRET"]
            self._save_to_env(data)

        else:
            logger.error("Refreshing token procedure failed.")
            logger.info(f"Details: {response.json()}")

    def check_token_expiration(self):
        logger.info(f"Checking if token is expired")
        if self._is_token_expired(self.loaded_tokens["EXPIRES_AT"]):
            logger.warning("Token is expired. Refresh token required.")
            self.refresh_token()
            time.sleep(5)
            self._load_tokens()
        else:
            logger.success("Token is not expired. Send API request allowed.")

    def activities_request(self):
        self.check_token_expiration()
        headers = {"Authorization": f"Bearer {self.loaded_tokens['ACCESS_TOKEN']}"}

        logger.info("Create datetime params. Please put your start and end date.")
        self.start_date = input("Start date in YYYY-MM-DD format")
        self.end_date = input("End date in YYYY-MM-DD format")

        after = int(time.mktime(time.strptime(self.start_date, '%Y-%m-%d')))
        before = int(time.mktime(time.strptime(self.end_date, '%Y-%m-%d')))
        params = {
            'after': after,
            'before': before,
            'per_page': 99
        }

        logger.info("Sending request...")
        response = requests.get(ACTIVITIES_URL, headers=headers, params=params)
        if response.status_code == 200:
            logger.success("Response from server received correctly.")
            self.activities = response.json()
            for activity in self.activities:
                print(f"ID: {activity['id']}, "
                      f"Datetime: {activity['start_date_local']}, "
                      f"Type: {activity['type']}, "
                      f"Distance: {activity['distance']/1000} km,")
            return self.activities
        else:
            logger.error("Response from server received incorrectly.", response.status_code, response.text)
            print("Error:", response.status_code, response.text)
            return None

    def _activity_details_request(self, activity_id):
        url = ONE_ACTIVITY_TEMPLATE.format(activity_id)
        headers = {"Authorization": f"Bearer {self.loaded_tokens['ACCESS_TOKEN']}"}
        params = {
            "keys": "heartrate,velocity_smooth",
            "key_by_type": "true",
        }

        logger.info(f"Sending request for {activity_id} ID...")
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            logger.success("Response from server received correctly.")
            return response.json()

        else:
            logger.error("Response from server received incorrectly.", response.status_code, response.text)
            print("Error:", response.status_code, response.text)
            return None

    def collect_required_data(self):
        self.activities_request()

        temp_dict = defaultdict(list)
        try:
            for element in self.activities:
                if element["type"] == "Run":
                    temp_dict[element["id"]] = [element["start_date_local"]]
        except TypeError as e:
            logger.error(f"Activities empty. Error: {e}")

        for key, value in temp_dict.items():
            temp_activity_details = self._activity_details_request(key)
            temp_dict[key].append(temp_activity_details["heartrate"]["data"])
            temp_dict[key].append(temp_activity_details["velocity_smooth"]["data"])
        logger.success("COLLECTING DATA FINISHED.")
        return temp_dict






