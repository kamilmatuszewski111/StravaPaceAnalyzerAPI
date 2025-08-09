import os
import tempfile
from contextlib import contextmanager

import pytest
from loguru import logger

from source.database import DataBaseEditor


@contextmanager
def mute_logger():
    logger.disable("")
    try:
        yield
    finally:
        logger.enable("")


activities_data = [
        (
                {
                'id': 10,
                'start_date': '2025-06-01 05:00:00',
                'sport_type': 'Run',
                'average_heartrate': 150.0,
                'average_speed': 5.5
                },
                {
                    'heartrate': {'data': [1,2,3,4,5,6]}
                }
        ),
        (
                {
                'id': 11,
                'start_date': '2025-06-02 01:00:00',
                'sport_type': 'Squash',
                'average_heartrate': 170,
                'average_speed': 0.1
                },
                {
                    'heartrate': {'data': [170, 170, 170]}
                }
        )
    ]

@pytest.fixture
def test_db():
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    path = temp_db.name
    temp_db.close()

    db = DataBaseEditor(path=path)
    yield db

    db.conn.close()
    os.remove(path)

@pytest.mark.parametrize("activity, data",activities_data)
def test_add_and_check_activity(test_db, activity, data):
    assert not test_db.check_if_data_exist(activity['id'])
    assert test_db.add_activity_to_db(activity, data)
    assert not test_db.add_activity_to_db({'kupa': 0}, {'kupa': 0})
    assert test_db.check_if_data_exist(activity['id'])

@pytest.mark.parametrize("activity, data",activities_data)
def test_clear_whole_database_yes(test_db, monkeypatch, activity, data):
    monkeypatch.setattr("builtins.input", lambda _: "y")

    with mute_logger():
        assert test_db.add_activity_to_db(activity, data)
    assert test_db.check_if_data_exist(activity['id'])
    assert test_db.clear_whole_database()
    assert not test_db.check_if_data_exist(activity['id'])

@pytest.mark.parametrize("activity, data",activities_data)
def test_clear_whole_database_no(test_db, monkeypatch, activity, data):
    monkeypatch.setattr("builtins.input", lambda _: "n")

    with mute_logger():
        assert test_db.add_activity_to_db(activity, data)
    assert test_db.check_if_data_exist(activity['id'])
    assert not test_db.clear_whole_database()
    assert test_db.check_if_data_exist(activity['id'])

@pytest.mark.parametrize("activity, data",activities_data)
def test_read_data_in_time_range_positive(test_db, activity, data):
    with mute_logger():
        test_db.add_activity_to_db(activity, data)
    assert test_db.read_data_in_time_range('2025-05-31', '2025-06-03')
    assert test_db.read_data_in_time_range('2025-06-01', '2025-06-02')

@pytest.mark.parametrize("activity, data",activities_data)
def test_read_data_in_time_range_negative(test_db, activity, data):
    with mute_logger():
        test_db.add_activity_to_db(activity, data)
    assert not test_db.read_data_in_time_range('2025-04-31', '2025-05-03') # April has no 31st
    assert not test_db.read_data_in_time_range('2025-04-15', '2025-05-03')
    assert not test_db.read_data_in_time_range('2025-Apr-15', '2025-05-03')
    assert not test_db.read_data_in_time_range('Monday', '2025-05-03')
    assert not test_db.read_data_in_time_range('2025-06-01', '2025-06-01')