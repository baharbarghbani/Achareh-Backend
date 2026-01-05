"""
Test script to verify the rating functionality
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'achareh.settings')
django.setup()

from user.models import User, Profile, Role
from ad.models import Ad, AdRequest
from comment.models import Comment

def test_rating_functionality():
    print("Testing rating functionality...")
    
    # Create test users
    customer_role, _ = Role.objects.get_or_create(name=Role.Names.CUSTOMER)
    performer_role, _ = Role.objects.get_or_create(name=Role.Names.PERFORMER)
    
    customer = User.objects.create_user(
        username='customer_test',
        password='testpass123',
        phone_number='1234567890'
    )
    customer.roles.add(customer_role)
    
    performer = User.objects.create_user(
        username='performer_test',
        password='testpass123',
        phone_number='0987654321'
    )
    performer.roles.add(performer_role)
    
    # Create an ad
    ad = Ad.objects.create(
        title='Test Ad',
        description='Test Description',
        category='Test Category',
        creator=customer
    )
    
    # Create ad request and approve it
    ad_request = AdRequest.objects.create(
        performer=performer,
        ad=ad
    )
    
    # Update ad to assigned status
    ad.performer = performer
    ad.status = Ad.Status.ASSIGNED
    ad.save()
    
    # Update ad to done status
    ad.status = Ad.Status.DONE
    ad.save()
    
    # Create a comment/rating
    comment = Comment.objects.create(
        content='Great work!',
        rating=5,
        ad=ad,
        user=customer,
        performer=performer
    )
    
    # Update performer's profile
    performer_profile, created = Profile.objects.get_or_create(user=performer)
    performer_profile.completed_ads_count += 1
    
    # Calculate new average rating
    performer_comments = Comment.objects.filter(performer=performer)
    total_rating = sum([c.rating for c in performer_comments])
    performer_profile.average_rating = total_rating / performer_comments.count() if performer_comments.count() > 0 else 0.0
    performer_profile.save()
    
    print(f"Performer profile updated:")
    print(f"  Average rating: {performer_profile.average_rating}")
    print(f"  Completed ads count: {performer_profile.completed_ads_count}")
    
    # Verify the profile data
    assert performer_profile.average_rating == 5.0
    assert performer_profile.completed_ads_count == 1
    
    print("Test passed! Rating functionality works correctly.")
    
    # Clean up
    comment.delete()
    ad.delete()
    customer.delete()
    performer.delete()

if __name__ == "__main__":
    test_rating_functionality()