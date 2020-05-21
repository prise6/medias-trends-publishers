from abc import ABC, abstractmethod
from typing import List
import logging
import hashlib
from mtpublishers import config
import mtpublishers.tools.data as data_tools

logger = logging.getLogger(__name__)

#
# Core Classes
#


class CategoryItems():

    def __init__(self, category: str, items: List[dict] = []):
        self._items = []
        self._category = None
        self.items = items
        self.category = category

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items: dict):
        """
        Items setter

        Waiting items with this given structure:
        items: [{
                'title': str,
                'imdb_id': str,
                'rating': float, # nullable
                'year': int, # nullable
                'cover_url': str, # nullable
                'score': float, # nullable
                'valid_date': datetime.datetime # nullable
                'genres': list, # nullable
                'language_codes': list # nullable
        }, ...]
        """
        if not isinstance(items, list):
            raise TypeError("items must be instance of list")
        self._items = items
        self.consolidate()

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category: str):
        if not isinstance(category, str):
            raise TypeError("Category must be instance of string")
        self._category = category

    @property
    def imdb_ids(self):
        return [item.get('imdb_id') for item in self.items if item.get('imdb_id', None)]

    def append(self, item: dict):
        self.items.append(item)
        return self

    def consolidate(self):
        for item in self.items:
            item['genres_emoji'] = data_tools.add_emojis_genre(item.get('genres', []))
            item['langs_flag'] = data_tools.add_emojis_language(item.get('language_codes', []))


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

    def __init__(self):
        super().__init__()
        self._category_items = {}
        self._informations = {}
        self._hash = None
        self._hash_file = config.get('hash', 'file')
        self._hash_exists = False

    @property
    def category_items(self):
        return self._category_items

    @category_items.setter
    def category_items(self, category_items: List[CategoryItems]):
        if not all([isinstance(c, CategoryItems) for c in category_items]):
            raise TypeError("category_items is a list containing instance of CategoryItems")
        self._category_items = {c.category: c for c in category_items}
        self.hash = self.create_hash()
        return self

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

    @property
    def informations(self):
        return self._informations

    @informations.setter
    def informations(self, informations: dict):
        if not isinstance(informations, dict):
            raise("informations must be instance of dict")
        self._informations = informations

    def add_information(self, key: str, value: str):
        self._informations[key] = value

    def get_movies(self):
        return self._category_items.get('movies', None)

    def get_series(self):
        return self._category_items.get('series', None)

    def create_hash(self):
        imdb_ids = []
        for cat_name, category in self.category_items.items():
            imdb_ids.extend(category.imdb_ids)
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

    movies = [
        {'title': 'title_1', 'imdb_id': '1234', 'rating': 7.2, 'year': 2020, 'cover_url': 'https://picsum.photos/200/300'},
        {'title': 'title_2', 'imdb_id': '3241', 'rating': 4.6, 'year': 2019, 'cover_url': 'https://picsum.photos/200/300'},
        {'title': 'title_1', 'imdb_id': '4231', 'rating': 6.3, 'year': 2020, 'cover_url': 'https://picsum.photos/200/300'},
    ]

    mt_data = MediasTrendsData()
    mt_data.category_items = [CategoryItems("movies", movies)]

    return mt_data


def data_from_sql():

    mt_data = MediasTrendsData()

    infos_sql = data_tools.read_sql("mediastrends_informations.sql")
    with data_tools.connect_sqlite(factory=None) as conn:
        for info_name, info_value in conn.execute(infos_sql):
            mt_data.add_information(info_name, info_value)

    movies = CategoryItems(category="movies")
    # category: movies
    try:
        sql = data_tools.read_sql("trending_movies.sql")
        conn = data_tools.connect_sqlite()
        with conn:
            for item in conn.execute(sql):
                movies.append(item)
    except Exception as err:
        logger.error("Error during movies sql: %s" % err)

    movies.consolidate()
    mt_data.category_items = [movies]

    return mt_data
