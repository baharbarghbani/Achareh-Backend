from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .models import Ad
from .serializer import AdSerializer, AdCreateSerializer, AdReadSerializer
from user.models import User
from rest_framework import status


class AdListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(creator=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdCreateSerializer
        return AdReadSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class AdRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(creator=self.request.user)
    
    def patch(self, request, *args, **kwargs):
        
        if 'status' in request.data:
            if request.data['status'] == Ad.Status.CANCELLED:
                return Response("آگهی لغو شده استو ")
            
class AdAssignPerformerAPIView(CreateAPIView):
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]


    def post(self, request):
        ad = get_object_or_404(Ad, pk=self.kwargs["pk"], creator=self.request.user)
        performer_id = request.data.get("performer_id")
        if performer_id is None:
            return Response({"detail": "performer_id is required."}, status=400)
        
        if ad.status in [Ad.Status.CANCELLED, Ad.Status.DONE]:
            return Response({"detail": "این آگهی قابل تخصیص نیست."}, status=400)
        performer = get_object_or_404(User, pk=performer_id)
        ad.performer = performer
        ad.status = Ad.Status.ASSIGNED
        ad.save(update_fields=["performer", "status"])
        
        return Response(AdSerializer(ad).data, status=status.HTTP_200_OK)

        




