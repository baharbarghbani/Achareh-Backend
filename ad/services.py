from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Ad, AdRequest


@transaction.atomic
def choose_ad_request(*, ad_id: int, request_id: int, user):
    # Lock the Ad row to prevent concurrent choose operations
    ad = Ad.objects.select_for_update().get(pk=ad_id)

    if ad.creator_id != user.id:
        raise PermissionDenied("فقط صاحب آگهی می‌تواند پیمانکار را انتخاب کند.")

    if ad.status != Ad.Status.OPEN:
        raise ValidationError("این آگهی در وضعیت باز نیست.")

    if ad.performer_id is not None:
        raise ValidationError("برای این آگهی قبلاً انجام‌دهنده انتخاب شده است.")

    # Lock the request row as well
    req = (
        AdRequest.objects.select_for_update()
        .select_related("performer", "ad")
        .get(pk=request_id, ad_id=ad.id)
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

    return req


@transaction.atomic
def report_ad_done(*, ad_id: int, user):
    ad = Ad.objects.select_for_update().get(pk=ad_id)

    if ad.performer_id != user.id:
        raise PermissionDenied("فقط انجام‌دهنده می‌تواند پایان کار را اعلام کند.")

    if ad.status != Ad.Status.ASSIGNED:
        raise ValidationError("این آگهی در وضعیت تخصیص شده نیست.")

    ad.status = Ad.Status.DONE_REPORTED
    ad.save(update_fields=["status"])
    return ad


@transaction.atomic
def confirm_ad_done(*, ad_id: int, user):
    ad = Ad.objects.select_for_update().get(pk=ad_id)

    if ad.creator_id != user.id:
        raise PermissionDenied("فقط صاحب آگهی می‌تواند پایان کار را تایید کند.")

    if ad.status != Ad.Status.DONE_REPORTED:
        raise ValidationError("این آگهی در وضعیت اعلام پایان کار نیست.")

    ad.status = Ad.Status.DONE
    ad.save(update_fields=["status"])
    return ad
