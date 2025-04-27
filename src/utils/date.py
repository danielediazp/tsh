from datetime import datetime


def get_date(dt: datetime) -> str:
    """Extract the date out of a datetime object in the M/D/Y format.

    Args:
        dt (datetime): the date as datetime object.

    Returns:
        str: date in the format M/D/Y
    """
    return dt.strftime("%m/%d/%Y")
