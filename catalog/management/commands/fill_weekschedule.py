from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from catalog.models import WeekSchedule


class Command(BaseCommand):
    help = 'Fill out all cells of a week schedule table'

    def handle(self, *args, **options):
        try:
            WeekSchedule.fill_table()
            self.stdout.write(self.style.SUCCESS('Done! The WeekSchedule table was successfully populated.'))
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Failed! You have probably already executed this command: {e}'))
