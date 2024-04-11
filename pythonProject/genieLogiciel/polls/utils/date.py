from datetime import date


def get_today_date():
    return f"{date.today().day} {date.today().month} {date.today().year}"
