from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Property, RecentActivity, RentProperty, Notifications
from .utils import get_payment_status_chart


@receiver(post_save, sender=Property)
@receiver(post_save, sender=RentProperty)
def create_recent_activity(sender, instance, created, **kwargs):
    """
    Signal receiver that creates recent activity records for Property and RentProperty instances.

    This function is triggered whenever a Property or RentProperty instance is saved. It creates
    recent activity records based on the type of instance and its status.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Model instance): The instance of the model that was saved.
        created (bool): A boolean indicating whether the instance was created.
        **kwargs: Additional keyword arguments.

    Actions:
        - Creates a recent activity record when a Property instance is created.
        - Creates a recent activity record when a RentProperty instance is created.
        - Creates a recent activity record when a RentProperty instance's status is updated to "paid".
    """

    # Create recent activity for Property instance
    if sender == Property and created:
        RecentActivity.objects.create(
            user=instance.user,
            property=instance,
            activity_type="add",
        )
    # Create recent activity for RentProperty instance
    elif sender == RentProperty:
        if created:
            RecentActivity.objects.create(
                user=instance.property.user,
                property=instance.property,
                activity_type="rent",
            )
        else:
            if instance.status == "paid":
                RecentActivity.objects.create(
                    user=instance.property.user,
                    property=instance.property,
                    activity_type="payment",
                )
            elif instance.status == "overdue":
                RecentActivity.objects.create(
                    user=instance.property.user,
                    property=instance.property,
                    activity_type="overdue",
                )


@receiver(post_save, sender=RecentActivity)
def handle_recent_activity(sender, instance, created, **kwargs):
    """
    Signal receiver that handles recent activities and overdue notifications when a RecentActivity instance is created.

    This function is triggered whenever a RecentActivity instance is saved. If the instance is newly created,
    it handles both recent activities and overdue notifications based on the activity_type.

    Args:
        sender (Model): The model class that sent the signal.
        instance (RecentActivity): The instance of the model that was saved.
        created (bool): A boolean indicating whether the instance was created.
        **kwargs: Additional keyword arguments.

    Actions:
        - Handles recent activities if the activity_type is not "overdue".
        - Creates a notification for the user if the activity_type is "overdue".
        - Sends the appropriate data to the user's WebSocket channel.
    """
    if created:
        channel_layer = get_channel_layer()

        # Handle recent activities and overdue notifications
        if instance.activity_type != "overdue":
            recent_activities = list(
                RecentActivity.objects.filter(user=instance.user)
                .exclude(activity_type="overdue")
                .order_by("-timestamp")[:10]
            )
            async_to_sync(channel_layer.group_send)(
                f"user_{instance.user.id}",
                {
                    "type": "send_recent_activities",
                    "recent_activities": recent_activities,
                },
            )
        else:
            Notifications.objects.create(
                user=instance.user,
                property=instance.property,
                message=_(f"Payment overdue for property"),
            )
            notifications = list(
                Notifications.objects.filter(user=instance.user, is_read=False)
            )
            async_to_sync(channel_layer.group_send)(
                f"user_{instance.user.id}",
                {
                    "type": "send_overdue_notifications",
                    "notifications": notifications,
                },
            )

    data = get_payment_status_chart(instance.user)

    async_to_sync(channel_layer.group_send)(
        f"user_{instance.user.id}",
        {
            "type": "send_payment_status_chart",
            "data": data,
        },
    )