from abc import ABC, abstractmethod
import logging
import logging.config
import mtpublishers.tools.config as cfg

logger = logging.getLogger(__name__)


#
# logger
#

logging.getLogger(__name__).addHandler(logging.NullHandler())

#
# Configuration
#

config = cfg.populate_config(cfg.init_config(), reload_=False)

#
# Core Classes
#


class Observer(ABC):

    @abstractmethod
    def update(self, subject):
        return

    @abstractmethod
    def __str__(self):
        return


class Subject(ABC):

    def __init__(self):
        self._observers = []

    def register_observer(self, observer: Observer):
        self._observers.append(observer)
        return self

    def unregister_observer(self, observer: Observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            logger.debug("Observer %s is not registered" % observer)
            pass

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class MediasTrendsData(Subject):

    def __init__(self, items: dict):
        super().__init__()
        self._items = None
        self._hash = None
        # going with setter
        self.items = items

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items: dict):
        """
        Items setter

        Waiting items with this given structure:
        items: {
            'category' : [{
                'name': str,
                'imdb_id': str,
                'rating': float, # nullable
                'year': int, # nullable
                'cover_url': str, # nullable
                'score': float, # nullable
                'valid_date': datetime.datetime # nullable
                'genre': str, # nullable
                'emojis': list, # nullable
            }]
        }
        """
        if not isinstance(items, dict):
            raise TypeError("items must be instance of dict")
        self._items = items

    @property
    def hash(self):
        if not self._hash:
            self.create_hash()
        return self._hash

    @hash.setter
    def hash(self, hash):
        self._hash = hash
        return self

    def get_movies(self):
        return self._items.get('movies', None)

    def get_series(self):
        return self._items.get('series', None)

    def create_hash(self):
        pass

    def save_hash(self):
        pass

    def hash_exist(self):
        pass

    def notify(self):
        if self.hash_exist(self):
            return
        super().notify()


class Publisher(Observer):

    def __init__(self):
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: MediasTrendsData):
        if not isinstance(data, MediasTrendsData):
            raise TypeError("Data must be instance of MediasTrendsData")
        self._data = data
        return self

    def update(self, data: MediasTrendsData):
        self.data = data
        return self.publish()

    @abstractmethod
    def publish(self):
        return

    def __str__(self):
        return self.__class__.__name__


#
# Classes instanciation
#

def data_from_static_gen():
    """Generate mediastrends data for tests
    """

    items = {
        'movies': [
            {'name': 'name_1', 'imdb_id': '1234', 'rating': 7.2, 'year': 2020, 'cover_url': 'https://picsum.photos/200/300'},
            {'name': 'name_2', 'imdb_id': '3241', 'rating': 4.6, 'year': 2019, 'cover_url': 'https://picsum.photos/200/300'},
            {'name': 'name_1', 'imdb_id': '4231', 'rating': 6.3, 'year': 2020, 'cover_url': 'https://picsum.photos/200/300'},
        ]
    }

    return MediasTrendsData(items)