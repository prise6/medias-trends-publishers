import logging
from mtpublishers.website import StaticWebsitePublisher
from mtpublishers.core import data_from_sql, data_from_static_gen

logger = logging.getLogger(__name__)


def publish(publishers: list, force: bool = False, test: bool = False, sql_data=True, **kwargs):
    publishers_call = {
        'website': StaticWebsitePublisher
    }

    if sql_data:
        data = data_from_sql()
    else:
        data = data_from_static_gen()

    if force:
        logger.debug("Force option is True: clear hash")
        data.clear_hash()

    for publisher in publishers:
        if publisher not in publishers_call:
            logger.debug("%s publisher doesn't exist" % publisher)
            continue

        publisher = publishers_call.get(publisher)()
        data.register_observer(publisher)
        logger.debug("publisher %s attached" % publisher)

    data.notify()
