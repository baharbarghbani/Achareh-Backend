from django.db.models import query
from rest_framework import generics
from .models import Ticket, TicketMessage
from .serializer import TicketSerializer
from rest_framework.permissions import IsAuthenticated
from user.utils import is_support
from .serializer import TicketSerializer, TicketMessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

# Create your views here.
class TicketListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ticket.objects.all()
        if is_support(self.request.user):
            return queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TicketMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TicketMessage.objetcs.filter(user=self.request.user)
    
class TicketMessageListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketMessageSerializer

    def get_ticket(self):
        ticket = get_object_or_404(Ticket, pk=self.kwargs["ticket_id"])

        if not is_support(self.request.user) and ticket.user_id != self.request.user.id:
            raise PermissionDenied("Not allowed.")
        return ticket

    def get_queryset(self):
        ticket = self.get_ticket()
        return TicketMessage.objects.filter(ticket=ticket).order_by("created_at")

    def perform_create(self, serializer):
        ticket = self.get_ticket()

        if ticket.status == Ticket.Status.CLOSED and not is_support(self.request.user):
            raise ValidationError({"detail": "Ticket is closed."})

        serializer.save(ticket=ticket, sender=self.request.user)



        


