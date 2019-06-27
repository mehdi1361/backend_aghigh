# !/usr/bin/env python
import pika

from django.conf import settings
from dashboard.singleton import Singleton


@Singleton
class RabbitmqConnection(object):
    __rc = None

    @classmethod
    def generate_connection(cls):
        if cls.__rc is None:
            credentials = pika.PlainCredentials(
                settings.RABBIT_MQ_USER,
                settings.RABBIT_MQ_PASS,
            )

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='localhost',
                    credentials=credentials
                )
            )
            cls.__rc = connection.channel()

        return cls.__rc

    def __init__(self):
        self.generate_connection()

    def get_connection(self):
        return self.__rc


