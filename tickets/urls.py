from django.urls import path
from .views import TicketListCreateAPIView, TicketRetrieveUpdateDeleteAPIView, TicketReplyAPIView

urlpatterns = [
    path("tickets/", TicketListCreateAPIView.as_view()),
    path("tickets/<int:pk>/", TicketRetrieveUpdateDeleteAPIView.as_view()),
    path("tickets/<int:pk>/reply/", TicketReplyAPIView.as_view()),
]