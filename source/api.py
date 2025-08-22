import time
from http import HTTPStatus
from typing import List, Optional, Union

import requests
from loguru import logger

from source.token_manager import TokenManager

ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
ONE_ACTIVITY_TEMPLATE = "https://www.strava.com/api/v3/activities/{}/streams"


class StravaAPI:
    """
    Provides methods to access Strava endpoints like activities and stream data.
    """

    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager

    def get_activities(self, start_date: str, end_date: str, activity_types: Optional[Union[str, List[str]]] = None):
        """
        Take user activities within a date range.

        :param start_date: Start date in 'YYYY-MM-DD'
        :param end_date: End date in 'YYYY-MM-DD'
        :param activity_types: Optional; str or list of activity types (e.g. "Run", ["Run", "Squash"])
        :return: List of filtered activities
        """
        logger.info(f"Getting {activity_types} activities from {start_date} to {end_date}")
        headers = {"Authorization": f"Bearer {self.token_manager.get_access_token()}"}
        after = int(time.mktime(time.strptime(start_date, "%Y-%m-%d")))
        before = int(time.mktime(time.strptime(end_date, "%Y-%m-%d")))

        response = requests.get(
            ACTIVITIES_URL, headers=headers, params={"after": after, "before": before, "per_page": 200}
        )
        if response.status_code == HTTPStatus.OK:
            logger.success("Successfully retrieved activities.")
            activities = response.json()
            if activity_types is None:
                return activities
            if isinstance(activity_types, str):
                activity_types = [activity_types]

            filtered_activities = [a for a in activities if a.get("sport_type") in activity_types]
            logger.info(f"Filtered {len(filtered_activities)} activities of type(s): {activity_types}")
            return filtered_activities
        else:
            logger.error(f"Error fetching activities: {response.status_code} - {response.text}")
            return []

    def get_activity_streams(self, activity_id: int):
        """
        Returns stream data (heartrate, velocity) for a specific activity.
        """
        logger.info(f"Getting stream data for activity {activity_id}")
        headers = {"Authorization": f"Bearer {self.token_manager.get_access_token()}"}
        response = requests.get(
            ONE_ACTIVITY_TEMPLATE.format(activity_id), headers=headers, params={"keys": "heartrate,velocity_smooth"}
        )
        if response.status_code == HTTPStatus.OK:
            return response.json()
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logger.error(
                f"Error fetching activity stream for {activity_id}: {response.status_code} - "
                f"{HTTPStatus.TOO_MANY_REQUESTS.description}"
            )
            logger.info(
                "Already downloaded activities will be saved in your database. "
                "Please wait 15 minutes for more requests."
            )
            return None
        else:
            logger.error(f"Error fetching activity stream for {activity_id}: {HTTPStatus(response.status_code)}")
            logger.info(f"{HTTPStatus(response.status_code).description}")
            return None
