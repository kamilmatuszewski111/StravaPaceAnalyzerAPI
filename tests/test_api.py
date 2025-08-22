from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from source.api import StravaAPI


@pytest.fixture
def token_manager_mock():
    mock = MagicMock()
    mock.get_access_token.return_value = "fake_access_token"
    return mock


@patch("source.api.requests.get")
def test_get_activities_pass(mock_get, token_manager_mock):
    fake_activities = [
        {"id": 1, "sport_type": "Run"},
        {"id": 2, "sport_type": "Ride"},
        {"id": 3, "sport_type": "Squash"},
    ]
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK.value
    mock_response.json.return_value = fake_activities
    mock_get.return_value = mock_response

    api = StravaAPI(token_manager_mock)

    result = api.get_activities("2025-01-01", "2025-01-02")
    assert result == fake_activities

    result = api.get_activities("2025-01-01", "2025-01-02", "Run")
    assert all(act["sport_type"] == "Run" for act in result)

    result = api.get_activities("2025-01-01", "2025-01-02", ["Ride", "Squash"])
    assert len(result) == 2


@patch("source.api.requests.get")
def test_get_activities_fail(mock_get, token_manager_mock):
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    mock_response.text = HTTPStatus.INTERNAL_SERVER_ERROR.name
    mock_get.return_value = mock_response

    api = StravaAPI(token_manager_mock)

    result = api.get_activities("2025-01-01", "2025-01-02")
    assert result == []


@patch("source.api.requests.get")
def test_get_activity_streams_pass(mock_get, token_manager_mock):
    fake_stream_data = {"heartrate": [100, 110], "velocity_smooth": [5, 5.5]}

    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK.value
    mock_response.json.return_value = fake_stream_data
    mock_get.return_value = mock_response

    api = StravaAPI(token_manager_mock)
    result = api.get_activity_streams(111)
    assert result == fake_stream_data


@patch("source.api.requests.get")
def test_get_activity_streams_fail(mock_get, token_manager_mock):
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.NOT_FOUND.value
    mock_get.return_value = mock_response

    api = StravaAPI(token_manager_mock)
    result = api.get_activity_streams(111)
    assert result is None
