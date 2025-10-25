import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async 
from .models import Job, Message, User # Import your models
from django.shortcuts import get_object_or_404

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when a WebSocket connection is established.
        Checks permissions and adds the user to a group for the job chat.
        """
        self.job_id = self.scope['url_route']['kwargs']['job_id']
        self.job_group_name = f'chat_{self.job_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return
        allowed_to_join = await self.check_user_permission(self.job_id, self.user)
        if not allowed_to_join:
            await self.close()
            return
        
        await self.channel_layer.group_add(self.job_group_name, self.channel_name)
        await self.accept()
        print(f"WebSocket connected: user {self.user.id} to job {self.job_id}")

        history = await self.get_message_history(self.job_id)
        await self.send(text_data=json.dumps({
            'type': 'message_history',
            'messages': history
        }))

    @database_sync_to_async
    def get_message_history(self, job_id, limit=50):
        """Fetches the most recent messages for a job."""
        try:
            job = Job.objects.get(id=job_id)
            messages = Message.objects.filter(job=job).order_by('-timestamp')[:limit][::-1]
            serialized_history = []
            for msg in messages:
                 serialized_history.append({
                     'id': msg.id,
                     'sender': msg.sender.id,
                     'sender_name': f"{msg.sender.first_name} {msg.sender.last_name}".strip() or msg.sender.username,
                     'receiver': msg.receiver.id,
                     'body': msg.body,
                     'timestamp': msg.timestamp.isoformat(),
                 })
            return serialized_history
        except Job.DoesNotExist:
            return []

    async def disconnect(self, close_code):
        """
        Called when the WebSocket connection is closed.
        Removes the user from the channel group.
        """
        print(f"WebSocket disconnected: user {self.user.id} from job {self.job_id}")
        await self.channel_layer.group_discard(
            self.job_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket (frontend).
        Saves the message to the database and broadcasts it to the group.
        """
        try:
            text_data_json = json.loads(text_data)
            message_body = text_data_json['message']

            if not message_body:
                return
            new_message = await self.save_message(message_body)
            if not new_message:
                print("Error saving message")
                return
            message_data = {
                'id': new_message.id,
                'sender': new_message.sender.id,
                'sender_name': await self.get_user_display_name(new_message.sender),
                'receiver': new_message.receiver.id,
                'body': new_message.body,
                'timestamp': new_message.timestamp.isoformat(),
            }
            await self.channel_layer.group_send(
                self.job_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
        except json.JSONDecodeError:
            print("Received invalid JSON")
        except KeyError:
            print("Received JSON missing 'message' key")
        except Exception as e:
            print(f"Error in receive: {e}")


    async def chat_message(self, event):
        """
        Called when a message needs to be sent *to* the WebSocket (frontend).
        Receives messages broadcast from the group send.
        """
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def check_user_permission(self, job_id, user):
        """
        Checks if the user is the customer or the hired pro for the job.
        Runs database queries in a synchronous thread.
        """
        try:
            job = Job.objects.select_related('accepted_bid__pro', 'customer').get(id=job_id)
            if job.accepted_bid and (user == job.customer or user == job.accepted_bid.pro):
                return True
        except Job.DoesNotExist:
            return False
        return False

    @database_sync_to_async
    def save_message(self, message_body):
        """
        Saves a message to the database. Determines the receiver.
        """
        try:
            job = Job.objects.select_related('accepted_bid__pro', 'customer').get(id=self.job_id)
            sender = self.user
            if sender == job.customer:
                receiver = job.accepted_bid.pro
            elif job.accepted_bid and sender == job.accepted_bid.pro:
                receiver = job.customer
            else:
                return None
            message = Message.objects.create(
                job=job,
                sender=sender,
                receiver=receiver,
                body=message_body
            )
            return message
        except Job.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error saving message to DB: {e}")
            return None

    @database_sync_to_async
    def get_user_display_name(self, user):
        """Gets the user's display name."""
        return f"{user.first_name} {user.last_name}".strip() or user.username