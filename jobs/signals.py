from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.urls import reverse
 # <--- 1. Import reverse

# CHANGE 'Job' TO WHATEVER YOUR ACTUAL MODEL NAME IS
from .models import Job 

# MATCH THE SENDER NAME HERE TOO
@receiver(post_save, sender=Job) 
def notify_job_creation(sender, instance, created, **kwargs):
    print(f"\n🚀🚨 BEEP BEEP! SIGNAL FIRED! 🚨🚀\n")

    if created:
        try:
            job_url = reverse('jobs:job_detail', args=[instance.id]) 

            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    "global_notifications",
                    {
                        "type": "send_notification",
                        "message": f"New Job Alert: {getattr(instance, 'worker_type', 'Worker')} needed!",
                        "job_title": getattr(instance, 'title', 'New Job Posted'),
                        "url": job_url # <--- 3. Send the URL to the browser
                    }
                )
        except Exception as e:
            print(f"Signal Error: {e}")