from datetime import datetime

from matplotlib import pyplot as plt

from extra_tools.fit_file_decoder import FitFileDecoder as fit_decoder


def time_converter_from_iso(date_time):
    dt = datetime.fromisoformat(date_time.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class DataAnalyzer:
    def __init__(self, activities_data):
        if not activities_data:
            raise ValueError("Cannot perform analyzing on empty data.")
        self.activities_data = activities_data

    def extract_date_and_hr(self):
        ms_to_kmh = 3.6
        pace = lambda x: str(fit_decoder.pace_calculate(x * ms_to_kmh)).replace("0:", "", 1)
        date = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        return [(date(activity[2]), pace(activity[5])) for activity in self.activities_data]

    @staticmethod
    def mmss_to_minutes(time):
        m, s = map(int, time.split(":"))
        return m + s / 60


class Plot:
    def __init__(self, dates, time):
        self.dates = dates
        self.time = time

    def show_plot(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.dates, self.time, marker="o", linestyle="-")
        plt.ylim(8, 4)
        plt.title("Pace in time")
        plt.xlabel("Date")
        plt.ylabel("Pace [min/km]")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
