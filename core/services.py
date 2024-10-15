from .models import Notifications
from django.template.loader import get_template


def clear_notification_service(user):
    """
    """
    Notifications.objects.filter(user=user).update(is_read=True)
    notifications = Notifications.objects.filter(user=user, is_read=False)
    notifications_html = get_template("includes/notifications.html").render(
        context={"notifications": notifications}
    )

    return notifications_html