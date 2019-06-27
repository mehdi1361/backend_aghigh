from __future__ import absolute_import

import logging

from raven.handlers.logging import SentryHandler


class CustomHandlerSentry(SentryHandler):
    def __init__(self, *args, **kwargs):
        dsn = kwargs.pop('dsn', None)

        self.tags = kwargs.pop('tags', None)

        logging.Handler.__init__(self, level=kwargs.get('level', logging.NOTSET))

        super(CustomHandlerSentry, self).__init__(dsn, **kwargs)