from django.db.models import query
from rest_framework import generics
from .models import Ticket, TicketMessage
from .serializer import TicketSerializer
from rest_framework.permissions import IsAuthenticated
from user.utils import is_support
from .serializer import TicketSerializer, TicketMessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

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
    
class TicketReplyAPIView(generics.ListCreateAPIView):

    serializer_class = TicketMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ticket = get_object_or_404(Ticket, pk=self.kwargs["pk"], user=self.request.user)
        return TicketMessage.objects.filter(ticket=ticket)

    def create(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=kwargs["pk"], user=request.user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        msg = TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            body=serializer.validated_data["body"]
        )

        return Response(TicketMessageSerializer(msg).data, status=status.HTTP_201_CREATED)




        


