from datetime import date


def get_today_date() -> str:
    return f"{date.today().day}/{date.today().month}/{date.today().year}"


def get_today_year() -> int:
    return date.today().year
