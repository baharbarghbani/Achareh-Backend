"""
Test script to verify the complete workflow:
1. User creates an ad
2. Performer submits request for the ad
3. Creator chooses the performer
4. Performer reports done
5. Creator approves and gives comment and rating
"""
import os
import django
from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from user.models import Profile, Role
from ad.models import Ad, AdRequest
from comment.models import Comment

User = get_user_model()

class CompleteWorkflowTest(APITestCase):
    def setUp(self):
        # Create roles
        self.customer_role, _ = Role.objects.get_or_create(name=Role.Names.CUSTOMER)
        self.performer_role, _ = Role.objects.get_or_create(name=Role.Names.PERFORMER)

        # Create customer user (ad creator)
        self.customer = User.objects.create_user(
            username='customer_test',
            password='testpass123',
            phone_number='1234567890'
        )
        self.customer.roles.add(self.customer_role)

        # Create performer user
        self.performer = User.objects.create_user(
            username='performer_test',
            password='testpass123',
            phone_number='0987654321'
        )
        self.performer.roles.add(self.performer_role)

        # Create client
        self.client = APIClient()

    def test_complete_workflow(self):
        """Test the complete workflow from ad creation to rating"""
        print("Step 1: Customer logs in and creates an ad")
        # Customer logs in
        login_successful = self.client.login(username='customer_test', password='testpass123')
        self.assertTrue(login_successful)

        # Customer creates an ad
        ad_data = {
            'title': 'Test Ad for Workflow',
            'description': 'Test Description for Workflow',
            'category': 'Test Category',
            'execution_time': '2026-01-10T10:00:00Z',
            'execution_location': 'Test Location'
        }
        response = self.client.post('/api/ads/', ad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ad_id = response.data['id']
        print(f"Ad created with ID: {ad_id}")

        print("Step 2: Performer logs in and submits request for the ad")
        # Performer logs in
        self.client.logout()
        login_successful = self.client.login(username='performer_test', password='testpass123')
        self.assertTrue(login_successful)

        # Performer submits request for the ad
        request_data = {}
        response = self.client.post(f'/api/ads/{ad_id}/requests/', request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        request_id = response.data['id']
        print(f"Request submitted with ID: {request_id}")

        print("Step 3: Customer logs in and chooses the performer")
        # Customer logs in again
        self.client.logout()
        login_successful = self.client.login(username='customer_test', password='testpass123')
        self.assertTrue(login_successful)

        # Customer chooses the performer
        response = self.client.post(f'/api/ads/{ad_id}/requests/{request_id}/choose/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Performer chosen successfully")

        # Verify ad status is now ASSIGNED
        response = self.client.get(f'/api/ads/{ad_id}/')
        self.assertEqual(response.data['status'], 'assigned')
        print(f"Ad status is now: {response.data['status']}")

        print("Step 4: Performer logs in and reports done")
        # Performer logs in
        self.client.logout()
        login_successful = self.client.login(username='performer_test', password='testpass123')
        self.assertTrue(login_successful)

        # Performer reports done
        response = self.client.post(f'/api/ads/{ad_id}/report-done/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Performer reported done")

        # Verify ad status is now DONE_REPORTED
        response = self.client.get(f'/api/ads/{ad_id}/')
        self.assertEqual(response.data['status'], 'done_reported')
        print(f"Ad status is now: {response.data['status']}")

        print("Step 5: Customer logs in and approves with rating")
        # Customer logs in
        self.client.logout()
        login_successful = self.client.login(username='customer_test', password='testpass123')
        self.assertTrue(login_successful)

        # Customer approves done and gives rating
        response = self.client.post(f'/api/ads/{ad_id}/confirm-done/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Customer confirmed done")

        # Verify ad status is now DONE
        response = self.client.get(f'/api/ads/{ad_id}/')
        self.assertEqual(response.data['status'], 'done')
        print(f"Ad status is now: {response.data['status']}")

        print("Step 6: Customer rates the performer")
        # Customer rates the performer
        rating_data = {
            'rating': 5,
            'content': 'Great job!'
        }
        response = self.client.post(f'/api/ads/{ad_id}/rate/', rating_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("Rating submitted successfully")

        # Verify performer's profile has the rating
        performer_profile = self.performer.profile
        self.assertEqual(performer_profile.average_rating, 5.0)
        print(f"Performer's average rating: {performer_profile.average_rating}")

        # Verify comment was created
        comments = Comment.objects.filter(performer=self.performer)
        self.assertEqual(comments.count(), 1)
        comment = comments.first()
        self.assertEqual(comment.rating, 5)
        self.assertEqual(comment.content, 'Great job!')
        print(f"Comment created: {comment.content}, Rating: {comment.rating}")

        print("Complete workflow test passed!")

    def tearDown(self):
        # Clean up
        User.objects.all().delete()
        Profile.objects.all().delete()
        Ad.objects.all().delete()
        AdRequest.objects.all().delete()
        Comment.objects.all().delete()
        Role.objects.all().delete()


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'achareh.settings')
    django.setup()
    import unittest
    # Run the test
    suite = unittest.TestLoader().loadTestsFromTestCase(CompleteWorkflowTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)