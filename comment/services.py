from user.models import Profile

def update_performer_rating(performer, new_rating):
    performer_profile, created = Profile.objects.get_or_create(user=performer)
    performer_profile.average_rating = (
        performer_profile.average_rating * performer_profile.rating_count + new_rating
    ) / (performer_profile.rating_count + 1)
    performer_profile.rating_count += 1
    performer_profile.save()


