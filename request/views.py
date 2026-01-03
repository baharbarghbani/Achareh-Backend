from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Request
from .serializer import RequestSerializer
from ad.models import Ad
from rest_framework.response import Response
from django.db.models import Q
from user.utils import is_performer
from ad.utils import is_open
from rest_framework import status

# Create your views here.  

class RequestListCreateAPIView(generics.ListCreateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ad = serializer.validated_data["ad"]
        if not is_performer(self.request.user):
            raise PermissionDenied("شما اجازه ثبت درخواست برای این آگهی را ندارید. نقش شما پیمانکار نیست." + str(is_performer(self.request.user)))

        if ad.creator_id == self.request.user.id:
            raise PermissionDenied("شما نمی‌توانید برای آگهی خودتان درخواست ثبت کنید.")
        if not is_open(ad):
            raise ValidationError({"ad": "این آگهی قابل درخواست نیست (باید باز باشد)."})
        if Request.objects.filter(ad=ad, performer=self.request.user).exists():
            raise ValidationError({"ad": "شما قبلاً برای این آگهی درخواست ثبت کرده‌اید."})
        serializer.save(performer=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Request.objects.filter(
            Q(ad__creator=user) | Q(performer=user)
        ).select_related("ad", "performer").order_by("-created_at")
    
    

class RequestRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]
    queryset = Request.objects.select_related("ad", "performer")

    def patch(self, request, *args, **kwargs):
        req_obj = self.get_object()      
        ad = req_obj.ad                  

        if ad.status != Ad.Status.OPEN:
            raise ValidationError({"detail": "این آگهی دیگر باز نیست."})

        new_status = request.data.get("status")
        if new_status not in [Request.Status.APPROVED, Request.Status.REJECTED]:
            raise ValidationError({"status": "فقط approved یا rejected مجاز است."})

        req_obj.status = new_status
        req_obj.save(update_fields=["status"])

        if new_status == Request.Status.APPROVED:
            ad.performer = req_obj.performer
            ad.status = Ad.Status.ASSIGNED
            ad.save(update_fields=["performer", "status"])
            Request.objects.filter(ad=ad).exclude(id=req_obj.id).update(status=Request.Status.REJECTED)

        return Response(RequestSerializer(req_obj).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        req_obj = self.get_object()
        ad = req_obj.ad

        if req_obj.performer_id != request.user.id:
            raise PermissionDenied("فقط پیمانکار می‌تواند درخواست خودش را حذف کند.")

        req_obj.delete()
        return Response({"detail": "درخواست حذف شد."}, status=200)

