from django.urls import path
from .views import TicketListCreateAPIView, TicketRetrieveUpdateDeleteAPIView, TicketMessageListCreateAPIView

urlpatterns = [
    path("tickets/", TicketListCreateAPIView.as_view()),
    path("tickets/<int:pk>/", TicketRetrieveUpdateDeleteAPIView.as_view()),
    path("tickets/<int:ticket_id>/messages/", TicketMessageListCreateAPIView.as_view()),

]