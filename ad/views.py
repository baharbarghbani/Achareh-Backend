from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Ad, AdRequest
from .serializer import (
    AdCreateSerializer,
    AdReadSerializer,
    AdUpdateSerializer,
    AdRequestCreateSerializer,
    AdRequestReadSerializer,
    AdRequestUpdateSerializer,
)
from user.utils import is_performer


# =========================
# Ads
# =========================

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
    """
    No Ad.status transitions here.
    Users can update only editable fields from AdUpdateSerializer.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Ad.objects.filter(Q(creator=user) | Q(performer=user))

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdReadSerializer
        if self.request.method in ["PATCH", "PUT"]:
            return AdUpdateSerializer
        return AdReadSerializer

    def patch(self, request, *args, **kwargs):
        # purely normal field update; Ad.status not handled here at all
        response = super().patch(request, *args, **kwargs)
        ad = self.get_object()
        return Response(AdReadSerializer(ad).data, status=response.status_code)


# =========================
# Requests (nested under Ad)
# =========================

class AdRequestListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_ad(self):
        return get_object_or_404(Ad, pk=self.kwargs["pk"])

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdRequestCreateSerializer
        return AdRequestReadSerializer

    def get_queryset(self):
        ad = self.get_ad()
        user = self.request.user

        # Creator sees all applicants
        if ad.creator_id == user.id:
            return ad.requests.all().order_by("-created_at")

        # Performer sees only their own request for this ad
        if is_performer(user):
            return ad.requests.filter(performer=user).order_by("-created_at")

        raise PermissionDenied("شما اجازه مشاهده درخواست‌های این آگهی را ندارید.")

    def perform_create(self, serializer):
        ad = self.get_ad()

        if not is_performer(self.request.user):
            raise PermissionDenied("شما پیمانکار نیستید.")
        if ad.creator_id == self.request.user.id:
            raise PermissionDenied("نمی‌توانید برای آگهی خودتان درخواست ارسال کنید.")
        if ad.status != Ad.Status.OPEN:
            raise ValidationError("این آگهی قابل درخواست نیست.")
        if ad.requests.filter(performer=self.request.user).exists():
            raise ValidationError("قبلاً درخواست داده‌اید.")

        serializer.save(performer=self.request.user, ad=ad)


class AdRequestRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    Single PATCH endpoint handles:
    - creator approves/rejects -> assigns performer and sets Ad.status=ASSIGNED
    - assigned performer reports done -> Ad.status=DONE_REPORTED
    - creator confirms done -> Ad.status=DONE
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return AdRequestUpdateSerializer
        return AdRequestReadSerializer

    def get_object(self):
        ad = get_object_or_404(Ad, pk=self.kwargs["pk"])
        req = get_object_or_404(AdRequest, pk=self.kwargs["request_pk"], ad=ad)
        return req

    def patch(self, request, *args, **kwargs):
        req = self.get_object()
        ad = req.ad
        user = request.user

        ser = AdRequestUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # ---- 1) Creator chooses performer by approving/rejecting a request ----
        if "status" in data:
            if ad.creator_id != user.id:
                raise PermissionDenied("فقط ایجادکننده آگهی می‌تواند درخواست را تایید/رد کند.")
            if ad.status != Ad.Status.OPEN:
                raise ValidationError("آگهی دیگر قابل تخصیص نیست.")

            new_status = data["status"]
            req.status = new_status
            req.save(update_fields=["status"])

            if new_status == AdRequest.Status.APPROVED:
                ad.performer = req.performer
                ad.status = Ad.Status.ASSIGNED
                ad.save(update_fields=["performer", "status"])

                AdRequest.objects.filter(ad=ad).exclude(id=req.id).update(
                    status=AdRequest.Status.REJECTED
                )

            return Response(AdRequestReadSerializer(req).data, status=200)

        # ---- 2) Assigned performer reports done ----
        if data.get("done_reported") is True:
            if ad.performer_id != user.id:
                raise PermissionDenied("فقط پیمانکار تخصیص داده شده می‌تواند پایان کار را اعلام کند.")
            if ad.status != Ad.Status.ASSIGNED:
                raise ValidationError("آگهی باید در وضعیت تخصیص شده باشد.")
            ad.status = Ad.Status.DONE_REPORTED
            ad.save(update_fields=["status"])
            return Response({"detail": "پایان کار اعلام شد."}, status=200)

        # ---- 3) Creator confirms done ----
        if data.get("done_confirmed") is True:
            if ad.creator_id != user.id:
                raise PermissionDenied("فقط ایجادکننده آگهی می‌تواند پایان کار را تایید کند.")
            if ad.status != Ad.Status.DONE_REPORTED:
                raise ValidationError("ابتدا پیمانکار باید پایان کار را اعلام کند.")
            ad.status = Ad.Status.DONE
            ad.save(update_fields=["status"])
            return Response({"detail": "پایان کار تایید شد."}, status=200)

        raise ValidationError("هیچ تغییری اعمال نشد.")


# =========================
# Performer requests list (flat)
# =========================

class RequestListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdRequestReadSerializer

    def get_queryset(self):
        if not is_performer(self.request.user):
            raise PermissionDenied("شما پیمانکار نیستید.")
        return AdRequest.objects.filter(performer=self.request.user).order_by("-created_at")
class OpenAdListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdReadSerializer

    def get_queryset(self):
        if not is_performer(self.request.user):
            raise PermissionDenied("فقط پیمانکار می‌تواند لیست آگهی‌های باز را مشاهده کند.")
        return Ad.objects.filter(status=Ad.Status.OPEN).order_by("-date_added")