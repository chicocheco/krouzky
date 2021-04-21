from django.core.management.base import BaseCommand
from catalog.models import WeekSchedule
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'Fill out all cells of a week schedule table'

    def handle(self, *args, **options):
        try:
            WeekSchedule.fill_table()
            self.stdout.write(self.style.SUCCESS('Done'))
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Table was probably already filled out: {e}'))
