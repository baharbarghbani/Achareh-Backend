from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch

from rest_framework.test import APIClient

from ad.models import Ad, AdRequest  # adjust import if your app name differs


User = get_user_model()


class AdsRequestsFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.creator = User.objects.create_user(
            username="creator", password="pass12345"
        )
        self.performer1 = User.objects.create_user(
            username="performer1", password="pass12345"
        )
        self.performer2 = User.objects.create_user(
            username="performer2", password="pass12345"
        )
        self.other_user = User.objects.create_user(
            username="other", password="pass12345"
        )

        # Create one OPEN ad by creator
        self.ad = Ad.objects.create(
            title="Test Ad",
            description="desc",
            category="cat",
            creator=self.creator,
            status=Ad.Status.OPEN,
        )

        # IMPORTANT: adjust these prefixes if your project uses different base path
        self.ads_base = "/api/ads/"
        self.open_ads_url = "/api/ads/open/"
        self.ad_requests_url = f"/api/ads/{self.ad.id}/requests/"
        # detail nested request url will be built after we create a request


    # ----------------------------
    # Helpers
    # ----------------------------
    def auth_as(self, user):
        self.client.force_authenticate(user=user)

    def unauth(self):
        self.client.force_authenticate(user=None)


    # ----------------------------
    # Ads tests
    # ----------------------------

    def test_creator_can_create_ad(self):
        self.auth_as(self.creator)
    
        payload = {"title": "A", "description": "B", "category": "C"}
        res = self.client.post(self.ads_base, payload, format="json")
        self.assertEqual(res.status_code, 201)
    
        # Response is from AdCreateSerializer (doesn't include creator)
        self.assertEqual(res.data["title"], "A")
    
        # Verify creator is correctly saved in DB
        ad = Ad.objects.get(title="A")
        self.assertEqual(ad.creator_id, self.creator.id)
        self.assertEqual(ad.status, Ad.Status.OPEN)
    @patch("ad.views.is_performer", return_value=True)
    def test_performer_can_list_open_ads(self, mock_is_perf):
        self.auth_as(self.performer1)

        res = self.client.get(self.open_ads_url)
        self.assertEqual(res.status_code, 200)

        # at least includes the ad we created
        ids = [item["id"] for item in res.data]
        self.assertIn(self.ad.id, ids)

    @patch("ad.views.is_performer", return_value=False)
    def test_non_performer_cannot_list_open_ads(self, mock_is_perf):
        self.auth_as(self.other_user)

        res = self.client.get(self.open_ads_url)
        self.assertEqual(res.status_code, 403)


    # ----------------------------
    # Requests tests
    # ----------------------------

    @patch("ad.views.is_performer", return_value=True)
    def test_performer_can_apply_to_open_ad(self, mock_is_perf):
        self.auth_as(self.performer1)

        # Your AdRequestCreateSerializer fields=[]
        res = self.client.post(self.ad_requests_url, {}, format="json")
        self.assertEqual(res.status_code, 201)

        self.assertTrue(
            AdRequest.objects.filter(ad=self.ad, performer=self.performer1).exists()
        )

    @patch("ad.views.is_performer", return_value=True)
    def test_creator_can_list_requests_for_ad(self, mock_is_perf):
        # Create a request first
        AdRequest.objects.create(ad=self.ad, performer=self.performer1)

        self.auth_as(self.creator)
        res = self.client.get(self.ad_requests_url)

        self.assertEqual(res.status_code, 200)
        # creator should see performer info (depending on serializer)
        self.assertGreaterEqual(len(res.data), 1)

    @patch("ad.views.is_performer", return_value=True)
    def test_performer_gets_only_their_request_in_ad_requests_list(self, mock_is_perf):
        AdRequest.objects.create(ad=self.ad, performer=self.performer1)
        AdRequest.objects.create(ad=self.ad, performer=self.performer2)

        self.auth_as(self.performer1)
        res = self.client.get(self.ad_requests_url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["performer_username"], self.performer1.username)


    # ----------------------------
    # Approve / reject (choosing performer)
    # ----------------------------

    @patch("ad.views.is_performer", return_value=True)
    def test_creator_can_approve_one_request_assigns_ad_and_rejects_others(self, mock_is_perf):
        r1 = AdRequest.objects.create(ad=self.ad, performer=self.performer1)
        r2 = AdRequest.objects.create(ad=self.ad, performer=self.performer2)

        self.auth_as(self.creator)

        url = f"/api/ads/{self.ad.id}/requests/{r1.id}/"
        res = self.client.patch(url, {"status": "approved"}, format="json")

        self.assertEqual(res.status_code, 200)

        # refresh from DB
        self.ad.refresh_from_db()
        r1.refresh_from_db()
        r2.refresh_from_db()

        self.assertEqual(self.ad.status, Ad.Status.ASSIGNED)
        self.assertEqual(self.ad.performer_id, self.performer1.id)
        self.assertEqual(r1.status, AdRequest.Status.APPROVED)
        self.assertEqual(r2.status, AdRequest.Status.REJECTED)

    @patch("ad.views.is_performer", return_value=True)
    def test_performer_cannot_approve_requests(self, mock_is_perf):
        r1 = AdRequest.objects.create(ad=self.ad, performer=self.performer1)

        self.auth_as(self.performer1)
        url = f"/api/ads/{self.ad.id}/requests/{r1.id}/"

        res = self.client.patch(url, {"status": "approved"}, format="json")
        self.assertEqual(res.status_code, 403)


    # ----------------------------
    # Done reported / done confirmed (no Ad.status patch)
    # ----------------------------

    @patch("ad.views.is_performer", return_value=True)
    def test_assigned_performer_can_report_done_changes_ad_status(self, mock_is_perf):
        r1 = AdRequest.objects.create(ad=self.ad, performer=self.performer1, status=AdRequest.Status.APPROVED)

        # simulate assignment like your approve flow does
        self.ad.performer = self.performer1
        self.ad.status = Ad.Status.ASSIGNED
        self.ad.save(update_fields=["performer", "status"])

        self.auth_as(self.performer1)

        url = f"/api/ads/{self.ad.id}/requests/{r1.id}/"
        res = self.client.patch(url, {"done_reported": True}, format="json")
        self.assertEqual(res.status_code, 200)

        self.ad.refresh_from_db()
        self.assertEqual(self.ad.status, Ad.Status.DONE_REPORTED)

    @patch("ad.views.is_performer", return_value=True)
    def test_creator_can_confirm_done_changes_ad_status(self, mock_is_perf):
        r1 = AdRequest.objects.create(ad=self.ad, performer=self.performer1, status=AdRequest.Status.APPROVED)

        self.ad.performer = self.performer1
        self.ad.status = Ad.Status.DONE_REPORTED
        self.ad.save(update_fields=["performer", "status"])

        self.auth_as(self.creator)
        url = f"/api/ads/{self.ad.id}/requests/{r1.id}/"

        res = self.client.patch(url, {"done_confirmed": True}, format="json")
        self.assertEqual(res.status_code, 200)

        self.ad.refresh_from_db()
        self.assertEqual(self.ad.status, Ad.Status.DONE)

    @patch("ad.views.is_performer", return_value=True)
    def test_non_assigned_performer_cannot_report_done(self, mock_is_perf):
        r1 = AdRequest.objects.create(ad=self.ad, performer=self.performer1)

        # Assign performer2 instead
        self.ad.performer = self.performer2
        self.ad.status = Ad.Status.ASSIGNED
        self.ad.save(update_fields=["performer", "status"])

        self.auth_as(self.performer1)
        url = f"/api/ads/{self.ad.id}/requests/{r1.id}/"

        res = self.client.patch(url, {"done_reported": True}, format="json")
        self.assertEqual(res.status_code, 403)
