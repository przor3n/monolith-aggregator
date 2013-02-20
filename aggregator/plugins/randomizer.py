import datetime
import random
from uuid import uuid1

from aggregator.plugins import Plugin
from aggregator.util import urlsafe_uuid


class RandomGenerator(Plugin):

    def __init__(self, **options):
        self.options = options

    def __call__(self, start_date, end_date):
        platforms = self.options.get('platforms')
        addons = int(self.options.get('addons', 100))
        if platforms is None:
            platforms = ('Mac OS X', 'Windows 8', 'Ubuntu')
        else:
            platforms = platforms.split(', ')

        uuids = {}
        for addon in range(addons):
            uuids[addon] = uuid1().hex

        for addon in range(addons):
            for delta in range((end_date - start_date).days):
                yield {'uid': urlsafe_uuid(),
                       'date': start_date + datetime.timedelta(days=delta),
                       'category': 'downloads',
                       'os': random.choice(platforms),
                       'downloads_count': random.randint(1000, 1500),
                       'users_count': random.randint(10000, 15000),
                       'add_on': addon + 1,
                       'app_uuid': uuids.get(addon)}
