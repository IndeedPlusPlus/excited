from datetime import datetime


def get_time_milliseconds(time=None):
    if time is None:
        time = datetime.now()
    delta = time - datetime(1970, 1, 1)
    return int(round(delta.total_seconds() * 1000))