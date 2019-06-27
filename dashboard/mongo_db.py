from pymongo import MongoClient
from django.conf import settings
from dashboard.singleton import Singleton


@Singleton
class MongoConnection(object):
    __db = None

    @classmethod
    def get_connection(cls):
        """Singleton method for running Mongo instance"""
        if cls.__db is None:
            # connection_string = "mongodb://{0}:{1}".format(MONGO_HOST, MONGO_PORT)
            cls.__db = MongoClient(
                host=settings.MONGO["HOST"], port=settings.MONGO["PORT"],
                serverSelectionTimeoutMS=2000, maxPoolSize=None
            )
        return cls.__db

    def __init__(self):
        self.get_connection()

    def getCursor(self, db):
        self.__db_cursor = self.__db[db]
        # self.__db_cursor.authenticate(settings.MONGO["USER"], settings.MONGO["PASS"], source='admin')
        return self.__db[db]


def MongoCursorDefs(db):
    return MongoConnection().getCursor(db)


# if settings.DEBUG:
#     cursor = ""
# else:
cursor = MongoCursorDefs('AGHIGH')
