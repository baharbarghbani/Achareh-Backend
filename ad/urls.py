from django.urls import path
from .views import (
    AdListCreateAPIView,
    AdRetrieveUpdateDestroyAPIView,
    OpenAdListAPIView,
    AdRequestListCreateAPIView,
    # AdRequestRetrieveUpdateAPIView,
    RequestListAPIView,
    AdRequestChooseAPIView,
    AdRequestDoneConfirmAPIView,
    AdRequestDoneReportAPIView,
    # AdFilterByRatingAPIView
)

urlpatterns = [
    path("ads/", AdListCreateAPIView.as_view()),
    path("ads/open/", OpenAdListAPIView.as_view()),
    path("ads/<int:pk>/", AdRetrieveUpdateDestroyAPIView.as_view()),

    path("ads/<int:pk>/requests/", AdRequestListCreateAPIView.as_view()),
    path("ads/<int:pk>/requests/<int:request_pk>/choose/", AdRequestChooseAPIView.as_view()),
    path("ads/<int:pk>/report-done/", AdRequestDoneReportAPIView.as_view()),
    path("ads/<int:pk>/confirm-done/", AdRequestDoneConfirmAPIView.as_view()),
    path("ads/requests/", RequestListAPIView.as_view()),
    # path("ads/filter-by-rating/", AdFilterByRatingAPIView.as_view()),
]
