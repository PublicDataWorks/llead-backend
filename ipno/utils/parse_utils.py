from datetime import date


def parse_date(year, month, day):
    if year and month and day:
        try:
            return date(
                int(year),
                int(month),
                int(day),
            )
        except ValueError or TypeError:
            return None


def parse_int(value):
    try:
        return int(float(value))
    except ValueError:
        return None
