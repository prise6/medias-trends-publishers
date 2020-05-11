import sqlite3
import logging
import os
import pathlib
from typing import Callable
from mtpublishers import config

logger = logging.getLogger(__name__)


def items_factory(cursor, row):
    d = {}
    fields = ['title', 'imdb_id', 'rating', 'year', 'cover_url',
              'score', 'valid_date', 'genre', 'emojis']
    for idx, col in enumerate(cursor.description):
        print(col)
        if col[0] in fields:
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
        con.row_factory = items_factory
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
