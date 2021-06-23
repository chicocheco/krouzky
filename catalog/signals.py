from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Course
from .utils import send_user_notification_created


@receiver(post_save, sender=Course, dispatch_uid='create')
def notify_approved(sender, instance, created, **kwargs):
    if created:
        send_user_notification_created(instance)
