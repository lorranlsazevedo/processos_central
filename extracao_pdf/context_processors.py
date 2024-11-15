from django.db.models import Count
from notifications.models import Notification


def notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, unread=True).count()
    else:
        count = 0
    return {'notifications_count': count}