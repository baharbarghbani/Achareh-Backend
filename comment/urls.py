from django.urls import path
from .views import CommentListCreateAPIView, CommentDetailAPIView, PerformerRatingListView

urlpatterns = [
    path('comments/', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailAPIView.as_view(), name='comment-detail'),
    path('performers/ratings/', PerformerRatingListView.as_view(), name='performer-rating-list'),
]