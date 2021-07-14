from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Course
from .utils import send_notification_course_registered


@receiver(post_save, sender=Course, dispatch_uid='create')
def course_registered(sender, instance, created, **kwargs):
    if created:
        send_notification_course_registered(instance)
