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
from django.db import transaction, IntegrityError
from django.db.models import Q

from .models import Ad, AdRequest
from .serializer import (
    AdCreateSerializer,
    AdReadSerializer,
    AdPatchSerializer,
    AdRequestCreateSerializer,
    AdRequestReadSerializer,
    AdRequestChooseSerializer,
)
from user.utils import is_performer

class AdListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(creator=self.request.user)

    def get_serializer_class(self):
        return AdCreateSerializer if self.request.method == "POST" else AdReadSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class AdRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Ad.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdReadSerializer
        if self.request.method == "PATCH":
            return AdPatchSerializer
        return AdPatchSerializer

    def patch(self, request, *args, **kwargs):
        user = request.user

        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        is_done_report = "done_reported" in data
        is_done_confirm = "done_confirmed" in data

        if is_done_report or is_done_confirm:
            with transaction.atomic():
                ad = (
                    Ad.objects.select_for_update()
                    .select_related("creator", "performer")
                    .get(pk=kwargs["pk"])
                )

                if is_done_report:
                    if ad.performer_id != user.id:
                        raise PermissionDenied("تنها پیمانکار مربوطه می‌تواند اتمام کار را اعلام کند.")
                    if ad.status != Ad.Status.ASSIGNED:
                        raise ValidationError("آگهی در وضعیت تخصیص یافته نیست.")

                    ad.status = Ad.Status.DONE_REPORTED
                    ad.save(update_fields=["status"])
                    return Response(AdReadSerializer(ad).data, status=200)

                # creator confirms done
                if is_done_confirm:
                    if ad.creator_id != user.id:
                        raise PermissionDenied("تنها خالق آگهی می‌تواند اتمام کار را تأیید کند.")
                    if ad.status != Ad.Status.DONE_REPORTED:
                        raise ValidationError("پیمانکار هنوز اتمام کار را اعلام نکرده است.")

                    ad.status = Ad.Status.DONE
                    ad.save(update_fields=["status"])
                    return Response(AdReadSerializer(ad).data, status=200)

        
        ad = self.get_object()
        if ad.creator_id != user.id:
            raise PermissionDenied("تنها خالق آگهی می‌تواند فیلدهای آگهی را به‌روزرسانی کند.")

        data.pop("done_reported", None)
        data.pop("done_confirmed", None)

        for field, value in data.items():
            setattr(ad, field, value)
        ad.save(update_fields=list(data.keys()))

        return Response(AdReadSerializer(ad).data, status=200)


class OpenAdListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdReadSerializer

    def get_queryset(self):
        if not is_performer(self.request.user):
            raise PermissionDenied("فقط پیمانکار می‌تواند لیست آگهی‌های باز را مشاهده کند.")
        return Ad.objects.filter(status=Ad.Status.OPEN).order_by("-date_added")

class AdRequestListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_ad(self):
        return get_object_or_404(Ad, pk=self.kwargs["pk"])

    def get_serializer_class(self):
        return AdRequestCreateSerializer if self.request.method == "POST" else AdRequestReadSerializer

    def get_queryset(self):
        ad = self.get_ad()
        user = self.request.user

        if ad.creator_id == user.id:
            return ad.requests.all().order_by("-created_at")

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

        # UX-friendly early check; still must guard DB-level uniqueness for concurrency.
        if ad.requests.filter(performer=self.request.user).exists():
            raise ValidationError("قبلاً درخواست داده‌اید.")

        try:
            serializer.save(performer=self.request.user, ad=ad)
        except IntegrityError:
            raise ValidationError("قبلاً درخواست داده‌اید.")


class AdRequestRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    Keep this endpoint *only* for choosing performer:
    PATCH /ads/<ad_id>/requests/<request_id>/ {"choose": true}
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return AdRequestReadSerializer if self.request.method == "GET" else AdRequestChooseSerializer

    def patch(self, request, *args, **kwargs):
        user = request.user

        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get("choose") is not True:
            raise ValidationError({"choose": "برای انتخاب پیمانکار باید choose=true ارسال شود."})

        with transaction.atomic():
            # Lock the Ad first to serialize selection.
            ad = Ad.objects.select_for_update().get(pk=self.kwargs["pk"])

            if ad.creator_id != user.id:
                raise PermissionDenied("Only the creator can choose a performer.")
            if ad.status != Ad.Status.OPEN:
                raise ValidationError("این آگهی در وضعیت باز نیست.")
            if ad.performer_id is not None:
                raise ValidationError("برای این آگهی قبلاً انجام‌دهنده انتخاب شده است.")

            # Lock the chosen request row too.
            req = (
                AdRequest.objects.select_for_update()
                .select_related("performer", "ad")
                .get(pk=self.kwargs["request_pk"], ad_id=ad.id)
            )

            if req.status != AdRequest.Status.PENDING:
                raise ValidationError("این درخواست قابل انتخاب نیست.")

            req.status = AdRequest.Status.APPROVED
            req.save(update_fields=["status"])

            ad.performer = req.performer
            ad.status = Ad.Status.ASSIGNED
            ad.save(update_fields=["performer", "status"])

            AdRequest.objects.filter(ad=ad).exclude(id=req.id).update(
                status=AdRequest.Status.REJECTED
            )

        return Response(AdRequestReadSerializer(req).data, status=200)


class RequestListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdRequestReadSerializer

    def get_queryset(self):
        if not is_performer(self.request.user):
            raise PermissionDenied("شما پیمانکار نیستید.")
        return AdRequest.objects.filter(performer=self.request.user).order_by("-created_at")
