from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Ticket, TicketMessage
from .serializer import (
    TicketListSerializer, 
    TicketDetailSerializer, 
    TicketCreateSerializer, 
    TicketReplySerializer
)
from user.permissions import IsSupportUser


class TicketListCreateAPIView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TicketCreateSerializer
        return TicketListSerializer
    
    def get_queryset(self):
        # Users can only see their own tickets
        return Ticket.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketSupportListAPIView(ListAPIView):
    """
    Endpoint for support users to see all tickets
    """
    permission_classes = [IsAuthenticated, IsSupportUser]
    serializer_class = TicketListSerializer
    queryset = Ticket.objects.all().order_by('-created_at')


class TicketSupportReplyAPIView(CreateAPIView):
    """
    Endpoint for support users to reply to a specific ticket
    """
    permission_classes = [IsAuthenticated, IsSupportUser]
    serializer_class = TicketReplySerializer
    
    def perform_create(self, serializer):
        ticket_id = self.kwargs['ticket_id']
        ticket = get_object_or_404(Ticket, id=ticket_id)
        serializer.save(
            sender=self.request.user,
            ticket=ticket
        )


class TicketDetailAPIView(RetrieveAPIView):
    """
    Endpoint for users to see details of their own ticket
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TicketDetailSerializer
    
    def get_queryset(self):
        # Users can only see their own tickets
        return Ticket.objects.filter(user=self.request.user)