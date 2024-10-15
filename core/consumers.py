# consumers.py

from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from datetime import datetime
from django.template.loader import get_template
from .models import RecentActivity, Notifications
from .services import *


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

    def receive(self, text_data):
        data = json.loads(text_data).get("data")
        
        if data == "clear":
            notifications_html = clear_notification_service(self.user)
            self.send(text_data=json.dumps({"notifications_html": notifications_html, "type": "clear_notifications"}))

    # Method to send the recent activities
    def send_recent_activities(self, event):
        if event["recent_activities"]:
            activities_html = get_template("includes/recent_activities.html").render(
                context={"recent_activities": event["recent_activities"]}
            )
            self.send(text_data=json.dumps({"activities_html": activities_html, "type": "recent_activities"}))

    # Method to send overdue notifications
    def send_overdue_notifications(self, event):
        if event["notifications"]:
            notifications_html = get_template("includes/notifications.html").render(
                context={"notifications": event["notifications"]}
            )
            self.send(text_data=json.dumps({"notifications_html": notifications_html, "type": "notifications"}))
