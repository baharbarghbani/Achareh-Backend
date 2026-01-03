from django.db import transaction
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import Request
from .serializer import RequestSerializer, RequestCreateSerializer, RequestReadSerializer
from ad.models import Ad

from user.utils import is_performer
from ad.utils import is_open


class RequestListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Request.objects
            .filter(Q(ad__creator=user) | Q(performer=user))
            .select_related("ad", "performer")
            .order_by("-created_at")
        )

        ad_id = self.request.query_params.get("ad")
        if ad_id:
            qs = qs.filter(ad_id=ad_id)
    
        return qs


    def get_serializer_class(self):
        if self.request.method == "POST":
            return RequestCreateSerializer
        return RequestReadSerializer

    def perform_create(self, serializer):
        ad = serializer.validated_data["ad"]

        # Only performers can apply
        if not is_performer(self.request.user):
            raise PermissionDenied("شما اجازه ثبت درخواست ندارید. نقش شما پیمانکار نیست.")

        # Cannot apply to own ad
        if ad.creator_id == self.request.user.id:
            raise PermissionDenied("شما نمی‌توانید برای آگهی خودتان درخواست ثبت کنید.")

        # Ad must be open
        if not is_open(ad) or ad.status != Ad.Status.OPEN:
            raise ValidationError({"ad": "این آگهی قابل درخواست نیست (باید باز باشد)."})

        # No duplicate
        if Request.objects.filter(ad=ad, performer=self.request.user).exists():
            raise ValidationError({"ad": "شما قبلاً برای این آگهی درخواست ثبت کرده‌اید."})

        serializer.save(performer=self.request.user)


class RequestRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Request.objects.select_related("ad", "performer")

    def get_serializer_class(self):
        # GET should be readable, PATCH should be updatable
        if self.request.method in ["GET"]:
            return RequestReadSerializer
        return RequestSerializer

    def patch(self, request, *args, **kwargs):
        req_obj = self.get_object()
        ad = req_obj.ad

        # Only ad creator can approve/reject
        if ad.creator_id != request.user.id:
            raise PermissionDenied("فقط ایجادکننده آگهی می‌تواند درخواست را تایید/رد کند.")

        # Must be open to assign
        if ad.status != Ad.Status.OPEN:
            raise ValidationError({"detail": "این آگهی دیگر باز نیست و قابل تخصیص نمی‌باشد."})

        new_status = request.data.get("status")
        if new_status not in [Request.Status.APPROVED, Request.Status.REJECTED]:
            raise ValidationError({"status": "فقط approved یا rejected مجاز است."})

        with transaction.atomic():
            req_obj.status = new_status
            req_obj.save(update_fields=["status"])

            # If approved -> assign the performer and update ad status (2.9)
            if new_status == Request.Status.APPROVED:
                ad.performer = req_obj.performer
                ad.status = Ad.Status.ASSIGNED
                ad.save(update_fields=["performer", "status"])

                # reject all other requests for the same ad
                Request.objects.filter(ad=ad).exclude(id=req_obj.id).update(status=Request.Status.REJECTED)

        return Response(RequestReadSerializer(req_obj).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        req_obj = self.get_object()
        ad = req_obj.ad

        # Only performer can delete their request
        if req_obj.performer_id != request.user.id:
            raise PermissionDenied("فقط پیمانکار می‌تواند درخواست خودش را حذف کند.")

        # Recommended: only allow delete while ad is still open
        if ad.status != Ad.Status.OPEN:
            raise ValidationError({"detail": "پس از تغییر وضعیت آگهی، امکان حذف درخواست وجود ندارد."})

        req_obj.delete()
        return Response({"detail": "درخواست حذف شد."}, status=status.HTTP_200_OK)
