from .models import Ad

def is_assigned(ad):
    return ad.status == Ad.Status.ASSIGNED

def is_open(ad):
    print(ad.status)
    print(Ad.Status.OPEN)
    return ad.status == Ad.Status.OPEN