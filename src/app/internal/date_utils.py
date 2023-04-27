import datetime
import holidays

korean_holidays = holidays.KR()


def is_weekends(value: datetime.date = datetime.date.today()) -> bool:
    return value.weekday() >= 5 or value in korean_holidays


def current_time() -> datetime.time:
    return datetime.datetime.now().time()
