from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .models import Ad
from .serializer import AdSerializer, AdCreateSerializer, AdReadSerializer, AdUpdateSerializer
from user.models import User
from rest_framework import status
from django.db.models import Q
from rest_framework.exceptions import ValidationError, PermissionDenied



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

        
class AdRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Ad.objects.filter(Q(creator=user) | Q(performer=user))

    def patch(self, request, *args, **kwargs):
        ad = self.get_object()

        if "status" not in request.data:
            return super().patch(request, *args, **kwargs)

        new_status = request.data.get("status")

        # 2.10 Performer reports done: assigned -> done_reported
        if new_status == Ad.Status.DONE_REPORTED:
            if ad.performer_id != request.user.id:
                raise PermissionDenied("فقط پیمانکار تخصیص داده شده می‌تواند پایان کار را اعلام کند.")
            if ad.status != Ad.Status.ASSIGNED:
                raise ValidationError({"detail": "آگهی باید در وضعیت تخصیص شده باشد."})
            ad.status = Ad.Status.DONE_REPORTED
            ad.save(update_fields=["status"])
            return Response(AdReadSerializer(ad).data, status=200)

        # 2.11 Customer confirms done: done_reported -> done
        if new_status == Ad.Status.DONE:
            if ad.creator_id != request.user.id:
                raise PermissionDenied("فقط ایجادکننده آگهی می‌تواند پایان کار را تایید کند.")
            if ad.status != Ad.Status.DONE_REPORTED:
                raise ValidationError({"detail": "ابتدا پیمانکار باید پایان کار را اعلام کند."})
            ad.status = Ad.Status.DONE
            ad.save(update_fields=["status"])
            return Response(AdReadSerializer(ad).data, status=200)

        if new_status == Ad.Status.CANCELLED:
            if ad.creator_id != request.user.id:
                raise PermissionDenied("فقط ایجادکننده آگهی می‌تواند آگهی را لغو کند.")
            if ad.status == Ad.Status.DONE:
                raise ValidationError({"detail": "آگهی انجام شده قابل لغو نیست."})
            ad.status = Ad.Status.CANCELLED
            ad.save(update_fields=["status"])
            return Response(AdReadSerializer(ad).data, status=200)

        raise ValidationError({"status": "تغییر وضعیت نامعتبر است."})




