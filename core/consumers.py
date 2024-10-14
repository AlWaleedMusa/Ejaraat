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
        html = get_template("includes/recent_activities.html").render(
            context={"recent_activities": event["recent_activities"]}
        )
        self.send(text_data=html)
