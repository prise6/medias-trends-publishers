from abc import ABC, abstractmethod
import logging
import hashlib
from mtpublishers import config
import mtpublishers.tools.data as data_tools

logger = logging.getLogger(__name__)

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
        self._hash_file = config.get('hash', 'file')
        self._hash_exists = False
        # going with setter
        self.items = items
        self.hash = self.create_hash()

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
                'title': str,
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
    def hash(self, hash_: str):
        if not isinstance(hash_, str):
            raise TypeError("Hash mu be instance of string")
        if self.open_hash() == hash_:
            self._hash_exists = True
        self._hash = hash_
        return self

    def get_movies(self):
        return self._items.get('movies', None)

    def get_series(self):
        return self._items.get('series', None)

    def create_hash(self):
        imdb_ids = []
        for category in self.items:
            imdb_ids.extend([item.get('imdb_id') for item in self.items.get(category) if item.get('imdb_id', None)])
        imdb_ids.sort()
        hash_object = hashlib.md5(''.join(imdb_ids).encode())
        return hash_object.hexdigest()

    def save_hash(self):
        with open(self._hash_file, 'w') as file_hash:
            file_hash.write(self.hash)

    def open_hash(self):
        hash_ = None
        try:
            with open(self._hash_file, 'r') as file_hash:
                hash_ = file_hash.read()
        except FileNotFoundError:
            pass
        return hash_

    def clear_hash(self):
        self._hash_exists = False

    def notify(self):
        if self._hash_exists:
            return
        super().notify()
        self.save_hash()


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
            {'title': 'title_1', 'imdb_id': '1234', 'rating': 7.2, 'year': 2020, 'cover_url': 'https://picsum.photos/200/300'},
            {'title': 'title_2', 'imdb_id': '3241', 'rating': 4.6, 'year': 2019, 'cover_url': 'https://picsum.photos/200/300'},
            {'title': 'title_1', 'imdb_id': '4231', 'rating': 6.3, 'year': 2020, 'cover_url': 'https://picsum.photos/200/300'},
        ]
    }

    return MediasTrendsData(items)


def data_from_sql():

    items = {"movies": [], "series": []}
    # category: movies
    try:
        sql = data_tools.read_sql("trending_movies.sql")
        conn = data_tools.connect_sqlite()
        with conn:
            for item in conn.execute(sql):
                items.get("movies").append(item)
    except Exception as err:
        logger.error("Error during movies sql: %s" % err)

    return MediasTrendsData(items)
