import requests
import time
from loguru import logger
import os
from dotenv import load_dotenv

TOKEN_URL = "https://www.strava.com/oauth/token"

class TokenManager:
    """
    Handles loading, saving, refreshing and validating Strava API tokens.
    """

    def __init__(self, env_file=".env"):
        self.env_file = env_file
        load_dotenv(dotenv_path=self.env_file, override=True)
        self.tokens = self._load_tokens()

    def _load_tokens(self):
        try:
            logger.info("Loading tokens...")
            load_dotenv(dotenv_path=self.env_file, override=True)
            return {
                "CLIENT_ID": int(os.getenv("CLIENT_ID")),
                "CLIENT_SECRET": os.getenv("CLIENT_SECRET"),
                "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN"),
                "REFRESH_TOKEN": os.getenv("REFRESH_TOKEN"),
                "EXPIRES_AT": int(os.getenv("EXPIRES_AT")),
            }
        except Exception as e:
            logger.error(f"Failed to load tokens from .env: {e}")
            raise

    def _save_tokens(self, updated_data: dict):
        """
        Save updated tokens to .env file.
        """
        logger.info("Saving tokens to .env")
        with open(self.env_file, "w") as f:
            for key, value in updated_data.items():
                f.write(f"{key.upper()}={value}\n")

    def is_expired(self) -> bool:
        return time.time() > self.tokens["EXPIRES_AT"]

    def refresh_access_token(self):
        """
        Refresh the ACCESS_TOKEN using the REFRESH_TOKEN.
        """
        logger.info("Refreshing access token...")
        response = requests.post(TOKEN_URL, data={
            "client_id": self.tokens["CLIENT_ID"],
            "client_secret": self.tokens["CLIENT_SECRET"],
            "refresh_token": self.tokens["REFRESH_TOKEN"],
            "grant_type": "refresh_token"
        })

        if response.status_code == 200:
            new_data = response.json()
            new_data["CLIENT_ID"] = self.tokens["CLIENT_ID"]
            new_data["CLIENT_SECRET"] = self.tokens["CLIENT_SECRET"]
            self._save_tokens(new_data)
            self.tokens = self._load_tokens()
            logger.success("Token refreshed successfully.")
        else:
            logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
            raise Exception("Unable to refresh access token.")

    def get_access_token(self) -> str:
        if self.is_expired():
            self.refresh_access_token()
        return self.tokens["ACCESS_TOKEN"]