from django.core.management.base import BaseCommand, CommandError
from apps.bagheri_api.views import BagheriApi
from dashboard.logger import logger_api
import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS('Start Sync Data'))
        logger_api.info('Start Sync Data {0}'.format(datetime.datetime.now()))

        # try:
        #     self.stdout.write(self.style.SUCCESS('Start change active user to False'))
        #     from apps.user.models.base import BaseUser
        #     BaseUser.objects.filter(user_is_test=False).update(is_active=False)
        #
        #     self.stdout.write(self.style.SUCCESS('End change active user to False'))
        # except:
        #     pass

        try:
            self.stdout.write(self.style.SUCCESS('Start Sync Teachers'))
            BagheriApi().set_teachers()
            self.stdout.write(self.style.SUCCESS('End Sync Teachers'))
        except:
            pass

        try:
            self.stdout.write(self.style.SUCCESS('Start Sync Provinces'))
            BagheriApi().set_provinces()
            self.stdout.write(self.style.SUCCESS('End Sync Provinces'))
        except:
            pass

        try:
            self.stdout.write(self.style.SUCCESS('Start Sync Counties'))
            BagheriApi().set_counties()
            self.stdout.write(self.style.SUCCESS('End Sync Counties'))
        except:
            pass

        try:
            self.stdout.write(self.style.SUCCESS('Start Sync Camps'))
            BagheriApi().set_camps()
            self.stdout.write(self.style.SUCCESS('End Sync Camps'))
        except:
            pass

        try:
        #     self.stdout.write(self.style.SUCCESS('Start Sync Schools'))
        #     from apps.league.models import School
        #     School.objects.all().update(active=False)
            BagheriApi().set_schools()
        #     self.stdout.write(self.style.SUCCESS('End Sync Schools'))
        except:
            pass

        try:
            self.stdout.write(self.style.SUCCESS('Start Sync Students'))
            BagheriApi().set_students()
            self.stdout.write(self.style.SUCCESS('End Sync Students'))
        except:
            pass

        self.stdout.write(self.style.SUCCESS('End Sync Data'))
        logger_api.info('End Sync Data {0}'.format(datetime.datetime.now()))
