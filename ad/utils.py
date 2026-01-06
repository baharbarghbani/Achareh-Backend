from .models import Ad

def is_assigned(ad):
    return ad.status == Ad.Status.ASSIGNED

def is_open(ad):
    print(ad.status)
    print(Ad.Status.OPEN)
    return ad.status == Ad.Status.OPEN

def calculate_rating(ratings, comment_counts):
    if comment_counts > 0:
        return sum([rating for rating in ratings])/ comment_counts
    return 0.0