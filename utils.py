import re
from datetime import datetime, timezone
from dateutil.parser import parse


def parseDateFromStr(date_str: str, timezone: str) -> datetime:
    if len(date_str) == 0:
        return datetime(0, 0, 0)

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
    if dates_diff < 0:
        return 0

    penalty = dates_diff // 7
    penalty = min(penalty, penalty_max)

    return penalty


def extract_taskid(logs):
    taskid_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z) TASKID is (\d+)'
    task_ids = []

    for line in logs.splitlines():
        match = re.match(taskid_pattern, line)
        if match:
            task_ids.append(int(match.group(2)))

    return task_ids


def extract_grading_reduction(logs):
    grading_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z) Grading reduced by (\d+)%'
    grading_reductions = []

    for line in logs.splitlines():
        match = re.match(grading_pattern, line)
        if match:
            grading_reductions.append(int(match.group(2)))

    return grading_reductions


def allValuesEqual(values: list) -> bool:
    if len(values) < 2:
        return True

    for i in range(1, len(values)):
        if values[i] != values[i - 1]:
            return False

    return True
