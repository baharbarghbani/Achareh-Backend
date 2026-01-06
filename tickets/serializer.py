from rest_framework import serializers
from .models import Ticket, TicketMessage
from user.models import User


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = TicketMessage
        fields = ['id', 'body', 'sender', 'sender_name', 'created_at']
        read_only_fields = ['sender', 'created_at']


class TicketListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    ad_title = serializers.CharField(source='ad.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'status', 'user', 'user_name', 'ad', 'ad_title', 'created_at']
        read_only_fields = ['user', 'created_at']


class TicketDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    ad_title = serializers.CharField(source='ad.title', read_only=True, allow_null=True)
    messages = TicketMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'status', 'user', 'user_name', 'ad', 'ad_title', 'created_at', 'messages']
        read_only_fields = ['user', 'created_at']


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['title', 'ad']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class TicketReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ['body']
    
    def create(self, validated_data):
        user = self.context['request'].user
        ticket_id = self.context['ticket_id']
        
        validated_data['sender'] = user
        validated_data['ticket_id'] = ticket_id
        
        # Update ticket status to PENDING when support replies
        ticket = Ticket.objects.get(id=ticket_id)
        if user.roles.filter(name='support').exists():
            ticket.status = Ticket.Status.PENDING
            ticket.save()
        
        return super().create(validated_data)