from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Property, RecentActivity, RentProperty
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime


@receiver(post_save, sender=Property)
def create_rent_history(sender, instance, created, **kwargs):
    if created:
        RecentActivity.objects.create(
            user=instance.user,
            property=instance,
            activity_type="add",
        )


@receiver(post_save, sender=RentProperty)
def create_rent_history(sender, instance, created, **kwargs):
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
        if instance.status == "overdue":
            RecentActivity.objects.create(
                user=instance.property.user,
                property=instance.property,
                activity_type="overdue",
            )


@receiver(post_save, sender=RecentActivity)
def send_recent_activities_update(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()

        if instance.activity_type == "overdue":
            notifications = list(
                RecentActivity.objects.filter(
                    user=instance.user, activity_type="overdue"
                )[:5]
            )
            async_to_sync(channel_layer.group_send)(
                f"user_{instance.user.id}",
                {
                    "type": "send_notifications",
                    "notifications": notifications,
                },
            )
            return
        else:
            recent_activities = list(
                RecentActivity.objects.filter(user=instance.user)
                .exclude(activity_type="overdue")
                .order_by("-timestamp")[:5]
            )
            async_to_sync(channel_layer.group_send)(
                f"user_{instance.user.id}",
                {
                    "type": "send_recent_activities",
                    "recent_activities": recent_activities,
                },
            )
