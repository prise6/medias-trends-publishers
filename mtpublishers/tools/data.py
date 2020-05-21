import sqlite3
import logging
import random
import os
import pathlib
from typing import Callable, List
from mtpublishers import config

logger = logging.getLogger(__name__)


def items_factory(cursor, row):
    d = {}
    fields = ['title', 'imdb_id', 'rating', 'year', 'cover_url',
              'score', 'valid_date', 'genres', 'language_codes']
    for idx, col in enumerate(cursor.description):
        if col[0] in fields:
            if col[0] in ['genres', 'language_codes']:
                d[col[0]] = row[idx].split(';') if isinstance(row[idx], str) else row[idx]
            else:
                d[col[0]] = row[idx]
    return d


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect_sqlite(database: str = None, factory: Callable = items_factory):
    """Connexion base de données Sqlite

    Args:
        database (str, optional): path to sqlite database. Defaults to None.

        If None, use config sqlite path paramater.

    Returns:
        Connection: connexion to db
    """
    database = database if database else config.get('sqlite', 'path')
    try:
        con = sqlite3.connect(database)
        if factory:
            con.row_factory = factory
    except sqlite3.OperationalError as err:
        logger.error("Error while getting connection to sqlite db: %s" % err)
        raise err

    return con


def read_sql(resource: str) -> str:
    """Read sql resource

    Args:
        resource (str): path to sql file (*.sql) or a string

    Returns:
        str: content of resource
    """
    sql = None

    if pathlib.Path(resource).suffix != '.sql':
        return resource

    candidats = [
        resource,
        os.path.join(config.get('directory', 'sql'), resource)
    ]

    for candidat in candidats:
        if os.path.exists(candidat) and os.path.isfile(candidat):
            try:
                with open(candidat, 'r') as sqlfile:
                    sql = sqlfile.read()
                    break
            except Exception:
                continue
    if not sql:
        raise ValueError("SQL resource not found")
    return sql


def add_emojis_genre(genres: List[str]):
    emojis = []

    if not genres:
        return emojis

    transform_genre = {
        'action': ['em-racing_car', 'em-female_superhero', 'em-male_superhero', 'em-boom', 'em-fire'],
        'adult': ['em-eggplant', 'em-peach', 'em-underage'],
        'adventure': ['em-world_map', 'em-mountain_railway', 'em-mag', 'em-railway_track'],
        'animation': ['em-teddy_bear', 'em-child'],
        'biography': ['em-book', 'em-bearded_person', 'em-lower_left_fountain_pen'],
        'comedy': ['em-face_with_hand_over_mouth', 'em-laughing', 'em-smile'],
        'crime': ['em-dagger_knife', 'em-female-detective', 'em-male-detective'],
        'documentary': ['em-national_park', 'em-elephant', 'em-film_projector'],
        'drama': ['em-cry', 'em-disappointed_relieved', 'em-anguished', 'em-confounded'],
        'family': ['em-family', 'em-woman-woman-girl-boy', 'em-man-man-girl-boy', 'em-man-woman-girl-boy'],
        'fantasy': ['em-male_mage', 'em-female_mage', 'em-dragon', 'em-unicorn_face'],
        'film-noir': ['em-black_circle', 'em-black_large_square'],
        'game-show': ['em-game_die'],
        'history': ['em-moyai', 'em-mantelpiece_clock'],
        'horror': ['em-scream', 'em-male_zombie', 'em-female_zombie', 'em-fearful', 'em-scream_cat'],
        'musical': ['em-notes', 'em-musical_keyboard', 'em-microphone'],
        'music': ['em-notes', 'em-musical_keyboard', 'em-microphone'],
        'mystery': ['em-shushing_face', 'em-zipper_mouth_face'],
        'news': ['em-newspaper', 'em-rolled_up_newspaper'],
        'reality-tv': ['em-tv'],
        'romance': ['em-two_hearts', 'em-woman-heart-man', 'em-woman-heart-woman', 'em-man-heart-man'],
        'sci-fi': ['em-alien', 'em-space_invader', 'em-spock-hand'],
        'short': None,
        'sport': ['em-baseball', 'em-football', 'em-swimmer', 'em-woman-biking', 'em-weight_lifter', 'em-soccer'],
        'talk-show': ['em-speaking_head_in_silhouette'],
        'thriller': ['em-cold_face', 'em-exploding_head'],
        'war': ['em-bomb', 'em-crossed_swords'],
        'western': ['em-desert', 'em-face_with_cowboy_hat', 'em-racehorse', 'em-cactus'],
    }

    for genre in genres:
        genre = genre.lower()
        if genre not in transform_genre:
            continue
        if not transform_genre.get(genre):
            continue
        em = random.choice(transform_genre.get(genre))
        emojis.append({'genre': genre, 'emoji': em})
    return emojis


def add_emojis_language(language_codes: List[str]):
    emojis = []
    transform_flag = {'en': 'gb', 'cmn': 'cn', 'hi': 'in', 'ja': 'jp',
                      'yue': 'cn', 'da': 'dk', 'ko': 'kr', 'el': 'gr',
                      'ny': 'mw'}
    pass_flags = ['haw', 'zxx']
    if not language_codes:
        return emojis

    for lang in language_codes:
        lang = lang.lower()
        if lang in pass_flags:
            continue
        lang = transform_flag.get(lang, lang)
        if lang in ['fr', 'gb', 'kr', 'jp', 'it', 'us', 'cn', 'de', 'es']:
            emojis.append('em-%s' % lang)
        else:
            emojis.append('em-flag-%s' % lang)
    return emojis
