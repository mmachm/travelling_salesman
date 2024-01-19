from datetime import date, datetime


def get_date_index(datecode: str, day_zero):
    return (
            datetime.strptime(datecode, "%d-%m-%Y").date() - day_zero
    ).days