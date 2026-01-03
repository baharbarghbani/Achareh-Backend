from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Request
from .serializer import RequestSerializer
from ad import Ad
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from user.models import Role

# Create your views here.  

class RequestListCreateAPIView(generics.ListCreateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ad = serializer.validated_data["ad"]
        if Role.Names.PERFORMER not in self.request.user.roles:
            raise PermissionDenied("شما اجازه ثبت درخواست برای این آگهی را ندارید.")

        if ad.creator_id == self.request.user.id:
            raise PermissionDenied("شما نمی‌توانید برای آگهی خودتان درخواست ثبت کنید.")
        if ad.status != Ad.Status.OPEN:
            raise ValidationError({"ad": "این آگهی قابل درخواست نیست (باید باز باشد)."})
        if Request.objects.filter(ad=ad, performer=self.request.user).exists():
            raise ValidationError({"ad": "شما قبلاً برای این آگهی درخواست ثبت کرده‌اید."})
        serializer.save(performer=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Request.objects.filter(
            Q(ad__creator=user) | Q(performer=user)
        ).select_related("ad", "performer").order_by("-created_at")

class RequestRetrieveAPIView(generics.ListAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ad_id = self.kwargs["ad_id"]
        ad = get_object_or_404(Ad, id=ad_id)

        if ad.creator_id != self.request.user.id:
            raise PermissionDenied("شما اجازه مشاهده درخواست‌های این آگهی را ندارید.")

        return Request.objects.filter(ad=ad).select_related("performer").order_by("-created_at")


class RequestDeleteAPIView(generics.DestroyAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        request_instance = self.get_object()
        if request_instance.ad.performer != request.user:
            return Response({"detail": "فقط ایجادکننده آگهی می‌تواند وضعیت درخواست را تغییر دهد."}, status=403)
        
        request_instance.delete()
        return Response({"detail": "درخواست شما لغو شد."}, status=200)

class RequestUpdateStatusAPIView(generics.UpdateAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]
    queryset = Request.objects.all()

    def update(self, request, *args, **kwargs):
        request_instance = self.get_object()
        if request_instance.ad.creator_id != request.user.id:
            raise PermissionDenied("فقط ایجادکننده آگهی می‌تواند وضعیت درخواست را تغییر دهد.")
        
        if request_instance.ad.status != Ad.Status.OPEN:
            raise ValidationError({"detail": "این آگهی دیگر باز نیست."})
        
        new_status = request.data.get("status")
        if new_status not in [Request.Status.APPROVED, Request.Status.REJECTED]:
            raise ValidationError({"status": "فقط accepted یا rejected مجاز است."})
        
        request_instance.status = new_status
        request_instance.save(update_fields=["status"])

        if new_status == Request.Status.APPROVED:
            request_instance.ad.performer = request_instance.performer
            request_instance.ad.status = Ad.Status.ASSIGNED
            request_instance.ad.save(update_fields=["performer", "status"])
            Request.objects.filter(ad=request_instance.ad).exclude(id=request_instance.id).update(status=Request.Status.REJECTED)

        return Response(RequestSerializer(request_instance).data, status=200)