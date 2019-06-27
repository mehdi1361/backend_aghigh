from django.core.management.base import BaseCommand, CommandError
from apps.emtiaz.compute import ComputingPoint


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Start Process School Point'))

        ComputingPoint().school_point()

        self.stdout.write(self.style.SUCCESS('End Process School Point'))

        self.stdout.write(self.style.SUCCESS('Start Process School Ranking'))

        ComputingPoint().school_ranking()

        self.stdout.write(self.style.SUCCESS('End Process School Ranking'))
