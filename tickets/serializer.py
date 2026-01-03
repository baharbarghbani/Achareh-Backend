from rest_framework import serializers
from .models import Ticket, TicketMessage

class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ['id','title', 'status', 'ad', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']


class TicketMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket', 'sender', 'body', 'created_at']
        read_only_fields = ["ticket", "sender", "created_at"] 




    