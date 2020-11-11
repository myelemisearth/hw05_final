import datetime


def current_year(request):
    current_date = datetime.datetime.now()
    return {'year': current_date.year}
