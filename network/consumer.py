import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Every user joins this "broadcast" group when they load the site
        self.group_name = "global_notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove them from the group when they close the tab
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # This handles the message sent from your jobs/signals.py
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'job_title': event['job_title'],
            'url': event.get('url', '#') # <--- Add this line!
        }))