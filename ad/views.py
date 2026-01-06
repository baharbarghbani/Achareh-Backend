from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
    CreateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from user.permissions import IsAdOwner, IsAdPerformer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from .models import Ad, AdRequest
from .serializer import (
    AdCreateSerializer,
    AdReadSerializer,
    AdUpdateSerializer,
    AdRequestCreateSerializer,
    AdRequestReadSerializer,
)
from comment.models import Comment
from user.models import Profile
from user.utils import is_performer, is_support
from .services import choose_ad_request, report_ad_done, confirm_ad_done

class AdListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if is_support(self.request.user):
            return Ad.objects.all()
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
        return AdUpdateSerializer

    def patch(self, request, *args, **kwargs):
        ad = self.get_object()

        if ad.creator_id != request.user.id:
            raise PermissionDenied("تنها خالق آگهی می‌تواند آگهی را به‌روزرسانی کند.")

        serializer = self.get_serializer(ad, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        ad = serializer.save()

        return Response(AdReadSerializer(ad).data, status=200)

    def put(self, request, *args, **kwargs):
        ad = self.get_object()

        if ad.creator_id != request.user.id:
            raise PermissionDenied("تنها خالق آگهی می‌تواند آگهی را به‌روزرسانی کند.")

        serializer = self.get_serializer(ad, data=request.data)
        serializer.is_valid(raise_exception=True)
        ad = serializer.save()

        return Response(AdReadSerializer(ad).data, status=200)

    def destroy(self, request, *args, **kwargs):
        ad = self.get_object()

        if ad.creator_id != request.user.id:
            raise PermissionDenied("تنها مالک آگهی می‌تواند آن را لغو کند.")

        if ad.status == Ad.Status.DONE:
            raise ValidationError("آگهی‌ای که انجام شده است را نمی‌توان لغو کرد.")

        ad.status = Ad.Status.CANCELLED
        ad.save(update_fields=["status"])
        return Response(status=204)


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

        base_qs = ad.requests.select_related("ad", "performer").order_by("-created_at")

        if ad.creator_id == user.id:
            return base_qs

        if is_performer(user):
            return base_qs.filter(performer=user)

        raise PermissionDenied("شما اجازه مشاهده درخواست‌های این آگهی را ندارید.")

    def perform_create(self, serializer):
        ad = self.get_ad()
        user = self.request.user

        if not is_performer(user):
            raise PermissionDenied("شما پیمانکار نیستید.")

        if ad.creator_id == user.id:
            raise PermissionDenied("نمی‌توانید برای آگهی خودتان درخواست ارسال کنید.")

        if ad.status != Ad.Status.OPEN:
            raise ValidationError("این آگهی قابل درخواست نیست.")

        if ad.requests.filter(performer=user).exists():
            raise ValidationError("قبلاً درخواست داده‌اید.")

        try:
            serializer.save(performer=user, ad=ad)
        except IntegrityError:
            raise ValidationError("قبلاً درخواست داده‌اید.")

class AdRequestChooseAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdOwner]
    serializer_class = AdRequestReadSerializer

    def post(self, request, *args, **kwargs):
        req = choose_ad_request(
            ad_id=kwargs["pk"],
            request_id=kwargs["request_pk"],
            user=request.user,
        )
        return Response(AdRequestReadSerializer(req).data, status=200)


class AdRequestDoneReportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdPerformer]
    serializer_class = AdReadSerializer

    def post(self, request, *args, **kwargs):
        ad = report_ad_done(
            ad_id=kwargs["pk"],
            user=request.user,
        )
        return Response(AdReadSerializer(ad).data, status=200)

class AdRequestDoneConfirmAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdOwner]
    serializer_class = AdReadSerializer

    def post(self, request, *args, **kwargs):
        ad = confirm_ad_done(
            ad_id=kwargs["pk"],
            user=request.user,
        )
        return Response(AdReadSerializer(ad).data, status=200)


# class AdRequestRetrieveUpdateAPIView(RetrieveUpdateAPIView):

#     permission_classes = [IsAuthenticated]

#     def get_serializer_class(self):
#         return AdRequestReadSerializer if self.request.method == "GET" else AdRequestChooseSerializer

#     def patch(self, request, *args, **kwargs):
#         user = request.user

#         serializer = self.get_serializer(data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         if serializer.validated_data.get("choose") is not True:
#             raise ValidationError({"choose": "برای انتخاب پیمانکار باید choose=true ارسال شود."})

#         with transaction.atomic():
#             ad = Ad.objects.select_for_update().get(pk=self.kwargs["pk"])

#             if ad.creator_id != user.id:
#                 raise PermissionDenied("Only the creator can choose a performer.")
#             if ad.status != Ad.Status.OPEN:
#                 raise ValidationError("این آگهی در وضعیت باز نیست.")
#             if ad.performer_id is not None:
#                 raise ValidationError("برای این آگهی قبلاً انجام‌دهنده انتخاب شده است.")

#             req = (
#                 AdRequest.objects.select_for_update()
#                 .select_related("performer", "ad")
#                 .get(pk=self.kwargs["request_pk"], ad_id=ad.id)
#             )

#             if req.status != AdRequest.Status.PENDING:
#                 raise ValidationError("این درخواست قابل انتخاب نیست.")

#             req.status = AdRequest.Status.APPROVED
#             req.save(update_fields=["status"])

#             ad.performer = req.performer
#             ad.status = Ad.Status.ASSIGNED
#             ad.save(update_fields=["performer", "status"])

#             AdRequest.objects.filter(ad=ad).exclude(id=req.id).update(
#                 status=AdRequest.Status.REJECTED
#             )

#         return Response(AdRequestReadSerializer(req).data, status=200)


class RequestListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdRequestReadSerializer

    def get_queryset(self):
        if not is_performer(self.request.user):
            raise PermissionDenied("شما پیمانکار نیستید.")
        return AdRequest.objects.filter(performer=self.request.user).order_by("-created_at")


