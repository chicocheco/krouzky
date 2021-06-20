from django.core.management.base import BaseCommand

from catalog.models import Course


class Command(BaseCommand):
    help = 'Changes status of any course to FINISHED if it is expired.'

    def handle(self, *args, **options):
        try:
            Course.mark_finished()
            self.stdout.write(self.style.SUCCESS('Done! Expired courses marked with a status FINISHED.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed! {e}'))
