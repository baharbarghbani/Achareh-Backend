from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Request
from .serializer import RequestSerializer
from ad.models import Ad
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from user.utils import is_performer
from .utils import is_approved, is_rejected
from ad.utils import is_assigned, is_open

# Create your views here.  

class RequestListCreateDestroyAPIView(generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ad = serializer.validated_data["ad"]
        if not is_performer(self.request.user):
            raise PermissionDenied("شما اجازه ثبت درخواست برای این آگهی را ندارید. نقش شما پیمانکار نیست." + str(is_performer(self.request.user)))

        if ad.creator_id == self.request.user.id:
            raise PermissionDenied("شما نمی‌توانید برای آگهی خودتان درخواست ثبت کنید.")
        if ad.status != is_open(ad):
            raise ValidationError({"ad": "این آگهی قابل درخواست نیست (باید باز باشد)."})
        if Request.objects.filter(ad=ad, performer=self.request.user).exists():
            raise ValidationError({"ad": "شما قبلاً برای این آگهی درخواست ثبت کرده‌اید."})
        serializer.save(performer=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Request.objects.filter(
            Q(ad__creator=user) | Q(performer=user)
        ).select_related("ad", "performer").order_by("-created_at")
    
    def destroy(self, request, *args, **kwargs):
        if self.ad.performer != request.user:
            return Response({"detail": "فقط ایجادکننده آگهی می‌تواند وضعیت درخواست را تغییر دهد."}, status=403)
        
        self.delete()
        return Response({"detail": "درخواست شما لغو شد."}, status=200)
    

class RequestRetrieveUpdateAPIView(generics.ListAPIView, generics.UpdateAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ad_id = self.kwargs["ad_id"]
        ad = get_object_or_404(Ad, id=ad_id)

        if ad.creator_id != self.request.user.id:
            raise PermissionDenied("شما اجازه مشاهده درخواست‌های این آگهی را ندارید.")

        return Request.objects.filter(ad=ad).select_related("performer").order_by("-created_at")
    
    def update(self, request, *args, **kwargs):
        if self.request.ad.creator_id != request.user.id:
            raise PermissionDenied("فقط ایجادکننده آگهی می‌تواند وضعیت درخواست را تغییر دهد.")
        
        if self.request.ad.status != is_open(self.request.ad):
            raise ValidationError({"detail": "این آگهی دیگر باز نیست."})
        
        new_status = request.data.get("status")
        if new_status not in [is_approved(self.request),is_rejected(self.request)]:
            raise ValidationError({"status": "فقط accepted یا rejected مجاز است."})
        
        self.request.status = new_status
        self.request.save(update_fields=["status"])

        if new_status == is_approved(self.request):
            self.request.ad.performer = self.request.performer
            self.request.ad.status = is_assigned(self.request.ad)
            self.request.ad.save(update_fields=["performer", "status"])
            Request.objects.filter(ad=self.request.ad).exclude(id=self.request.id).update(status=Request.Status.REJECTED)

        return Response(RequestSerializer(self.request).data, status=200)



