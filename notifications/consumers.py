from channels.generic.websocket import AsyncJsonWebsocketConsumer

class EventConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.room_group_name = f"event_{self.event_id}"

        # Join event room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave event room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        pass

    async def event_status_update(self, event):
        await self.send_json({
            "type": "status_update",
            "event_id": event["event_id"],
            "title": event["title"],
            "status": event["status"],
            "status_display": event["status_display"],
        })

    async def event_quota_update(self, event):
        await self.send_json({
            "type": "quota_update",
            "event_id": event["event_id"],
            "tickets": event["tickets"]
        })
