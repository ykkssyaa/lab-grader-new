from datetime import datetime, timezone
from dateutil.parser import parse


def parseDateFromStr(date_str: str, timezone: str) -> datetime:

    if len(date_str) == 0:
        return datetime(0,0,0)

    if len(date_str.split('.')) == 2:
        date_str += f'{datetime.now().year}'

    # add hours, minutes and seconds based on Moscow time
    date_str += ' 23:59:59 ' + timezone

    try:
        parsed_date = parse(date_str, dayfirst=True)
        return parsed_date
    except (ValueError, TypeError):
        return None


def calculatePenalty(dates_diff: int, penalty_max: int):
    penalty = dates_diff // 7
    penalty = min(penalty, penalty_max)

    return penalty
