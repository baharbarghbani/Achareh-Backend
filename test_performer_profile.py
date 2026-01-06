"""
Test script to verify the PerformerProfileAPIView functionality
"""
import os
import django
import unittest
from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from user.models import Profile, Role
from ad.models import Ad
from comment.models import Comment

User = get_user_model()

class PerformerProfileAPITest(APITestCase):
    def setUp(self):
        # Create roles
        self.customer_role, _ = Role.objects.get_or_create(name=Role.Names.CUSTOMER)
        self.performer_role, _ = Role.objects.get_or_create(name=Role.Names.PERFORMER)

        # Create users
        self.customer = User.objects.create_user(
            username='customer_test',
            password='testpass123',
            phone_number='1234567890'
        )
        self.customer.roles.add(self.customer_role)

        self.performer = User.objects.create_user(
            username='performer_test',
            password='testpass123',
            phone_number='0987654321'
        )
        self.performer.roles.add(self.performer_role)

        # Create performer profile
        self.performer_profile, _ = Profile.objects.get_or_create(user=self.performer)

        # Create ads for the performer
        self.ad1 = Ad.objects.create(
            title='Test Ad 1',
            description='Test Description 1',
            category='Test Category',
            creator=self.customer,
            performer=self.performer,
            status=Ad.Status.DONE
        )

        self.ad2 = Ad.objects.create(
            title='Test Ad 2',
            description='Test Description 2',
            category='Test Category',
            creator=self.customer,
            performer=self.performer,
            status=Ad.Status.DONE
        )

        self.ad3 = Ad.objects.create(
            title='Test Ad 3',
            description='Test Description 3',
            category='Test Category',
            creator=self.customer,
            performer=self.performer,
            status=Ad.Status.ASSIGNED  # Not completed
        )

        # Create client
        self.client = APIClient()

    def test_performer_profile_api_view(self):
        """Test that the PerformerProfileAPIView returns correct data"""
        # Login as the performer to satisfy authentication
        login_successful = self.client.login(username='performer_test', password='testpass123')
        self.assertTrue(login_successful)

        # Access the performer profile API endpoint
        url = f'/users/profile/performer/{self.performer_profile.id}/'
        response = self.client.get(url)

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response contains expected fields
        self.assertIn('id', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('completed_ads', response.data)
        self.assertIn('comments', response.data)

        # Check that the completed ads count is correct (should be 2)
        self.assertEqual(response.data['completed_ads'], 2)

        # Check that the profile id matches
        self.assertEqual(response.data['id'], self.performer_profile.id)

    def test_performer_profile_with_no_completed_ads(self):
        """Test the API when performer has no completed ads"""
        # Create another performer with no completed ads
        new_performer = User.objects.create_user(
            username='new_performer',
            password='testpass123',
            phone_number='1111111111'
        )
        new_performer.roles.add(self.performer_role)
        new_profile, _ = Profile.objects.get_or_create(user=new_performer)

        # Login as the new performer
        self.client.login(username='new_performer', password='testpass123')

        # Access the performer profile API endpoint
        url = f'/users/profile/performer/{new_profile.id}/'
        response = self.client.get(url)

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that completed ads count is 0
        self.assertEqual(response.data['completed_ads'], 0)

    def tearDown(self):
        # Clean up
        User.objects.all().delete()
        Profile.objects.all().delete()
        Ad.objects.all().delete()
        Role.objects.all().delete()


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'achareh.settings')
    django.setup()
    # Run the test
    suite = unittest.TestLoader().loadTestsFromTestCase(PerformerProfileAPITest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)