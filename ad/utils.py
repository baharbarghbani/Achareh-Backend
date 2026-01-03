from .models import Ad

def is_assigned(ad):
    return ad.status == Ad.Status.ASSIGNED

def is_open(ad):
    return ad.status == Ad.Status.OPEN