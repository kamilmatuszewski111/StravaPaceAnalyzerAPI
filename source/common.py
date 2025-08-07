from datetime import datetime

def time_converter_from_iso(date_time):
    dt = datetime.fromisoformat(date_time.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d %H:%M:%S')

class DataAnalyzer:
    def __init__(self, data):
        self.data = data

    def extract_list_of_data(self):
        for row in self.data:
            yield row
        # TODO: dokończyć wsyztsko tutaj