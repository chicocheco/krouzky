from django.core.management.base import BaseCommand

from invitations.models import Invitation


class Command(BaseCommand):
    help = 'Remove accepted or expired invitations.'

    def handle(self, *args, **options):
        try:
            Invitation.objects.delete_expired()
            self.stdout.write(self.style.SUCCESS('Done! Accepted or expired invitations were removed.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed! {e}'))
