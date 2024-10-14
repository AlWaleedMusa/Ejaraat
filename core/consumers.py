# consumers.py

from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from datetime import datetime
from django.template.loader import get_template


class RecentActivitiesConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            self.close()
            return
        else:
            self.user_id = self.user.id
            async_to_sync(self.channel_layer.group_add)(
                f"user_{self.user_id}", self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(
                f"user_{self.user_id}", self.channel_name
            )

    # Method to send the recent activities
    def send_recent_activities(self, event):
        if event["recent_activities"]:
            activities_html = get_template("includes/recent_activities.html").render(
                context={"recent_activities": event["recent_activities"]}
            )
            self.send(text_data=activities_html)

    def send_notifications(self, event):
        if event["notifications"]:
            notifications_html = get_template("includes/notifications.html").render(
                context={"notifications": event["notifications"]}
            )
            self.send(text_data=notifications_html)
