from .models import Request
def is_approved(request):
    return request.status == Request.Status.APPROVED

def is_rejected(request):
    return request.status == Request.Status.REJECTED

