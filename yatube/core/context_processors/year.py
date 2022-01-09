from datetime import datetime


def year(reuest):
    year = datetime.now().year
    return {'year': year}
