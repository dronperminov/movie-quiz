import calendar
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple


def get_month_range(year: int, month: int) -> Tuple[datetime, datetime]:
    start_date = datetime(year, month, 1, 0, 0, 0)
    _, num_days = calendar.monthrange(start_date.year, start_date.month)
    end_date = datetime(start_date.year, start_date.month, num_days, 23, 59, 59)
    return start_date, end_date


def parse_dates(date: str) -> Optional[Tuple[datetime, datetime]]:
    today = datetime.now()

    if date == "today":
        start_date = datetime(today.year, today.month, today.day, 0, 0, 0)
        end_date = datetime(today.year, today.month, today.day, 23, 59, 59)
        return start_date, end_date

    if date == "curr-month":
        start_date = datetime(today.year, today.month, 1, 0, 0, 0)
        end_date = datetime(today.year, today.month, today.day, 23, 59, 59)
        return start_date, end_date

    if date == "last-month":
        month, year = (today.month - 1, today.year) if today.month > 1 else (12, today.year - 1)
        return get_month_range(year=year, month=month)

    if date == "curr-year":
        start_date = datetime(today.year, 1, 1, 0, 0, 0)
        end_date = datetime(today.year, today.month, today.day, 23, 59, 59)
        return start_date, end_date

    if date == "last-year":
        start_date = datetime(today.year - 1, 1, 1, 0, 0, 0)
        end_date = datetime(today.year - 1, 12, 31, 23, 59, 59)
        return start_date, end_date

    if match := re.fullmatch(r"last-(?P<days>\d+)days", date):
        start_date = datetime(today.year, today.month, today.day, 0, 0, 0) - timedelta(days=int(match.group("days")))
        end_date = datetime(today.year, today.month, today.day, 23, 59, 59)
        return start_date, end_date

    if match := re.fullmatch(r"(?P<day1>\d\d?)-(?P<day2>\d\d?)", date):
        start_date = datetime(today.year, today.month, int(match.group("day1")), 0, 0, 0)
        end_date = datetime(today.year, today.month, int(match.group("day2")), 23, 59, 59)
        return min(start_date, end_date), max(start_date, end_date)

    if match := re.fullmatch(r"(?P<day1>\d\d?).(?P<month1>\d\d?)-(?P<day2>\d\d?).(?P<month2>\d\d?)", date):
        start_date = datetime(today.year, int(match.group("month1")), int(match.group("day1")), 0, 0, 0)
        end_date = datetime(today.year, int(match.group("month2")), int(match.group("day2")), 23, 59, 59)
        return min(start_date, end_date), max(start_date, end_date)

    if match := re.fullmatch(r"(?P<day1>\d\d?).(?P<month1>\d\d?).(?P<year1>\d\d\d\d)-(?P<day2>\d\d?).(?P<month2>\d\d?).(?P<year2>\d\d\d\d)", date):
        start_date = datetime(int(match.group("year1")), int(match.group("month1")), int(match.group("day1")), 0, 0, 0)
        end_date = datetime(int(match.group("year2")), int(match.group("month2")), int(match.group("day2")), 23, 59, 59)
        return min(start_date, end_date), max(start_date, end_date)

    if match := re.fullmatch(r"(?P<day>\d\d?).(?P<month>\d\d?)", date):
        start_date = datetime(today.year, int(match.group("month")), int(match.group("day")), 0, 0, 0)
        end_date = datetime(today.year, int(match.group("month")), int(match.group("day")), 23, 59, 59)
        return start_date, end_date

    if match := re.fullmatch(r"(?P<day>\d\d?).(?P<month>\d\d?).(?P<year>\d\d\d\d)", date):
        start_date = datetime(int(match.group("year")), int(match.group("month")), int(match.group("day")), 0, 0, 0)
        end_date = datetime(int(match.group("year")), int(match.group("month")), int(match.group("day")), 23, 59, 59)
        return start_date, end_date

    rus2month = {
        "январь": 1, "февраль": 2, "март": 3, "апрель": 4, "май": 5, "июнь": 6,
        "июль": 7, "август": 8, "сентябрь": 9, "октябрь": 10, "ноябрь": 11, "декабрь": 12
    }

    if match := re.fullmatch(fr'(?P<month>({"|".join(rus2month)}))', date):
        return get_month_range(year=today.year, month=rus2month[match.group("month")])

    if match := re.fullmatch(fr'(?P<month>({"|".join(rus2month)}))-(?P<year>\d\d\d\d)', date):
        return get_month_range(year=int(match.group("year")), month=rus2month[match.group("month")])

    return None
