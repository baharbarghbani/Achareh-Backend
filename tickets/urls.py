from django.urls import path
from .views import (
    TicketListCreateAPIView,
    TicketSupportListAPIView,
    TicketSupportReplyAPIView,
    TicketDetailAPIView
)

urlpatterns = [
    # User endpoints - users can create tickets and see their own tickets
    path('tickets/', TicketListCreateAPIView.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', TicketDetailAPIView.as_view(), name='ticket-detail'),
    
    # Support endpoints - only support users can see all tickets and reply
    path('tickets/support/', TicketSupportListAPIView.as_view(), name='ticket-support-list'),
    path('tickets/<int:ticket_id>/reply/', TicketSupportReplyAPIView.as_view(), name='ticket-support-reply'),
]