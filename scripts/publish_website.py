"""
Minimal script to create index.html page
"""
import logging
from mtpublishers.website import StaticWebsitePublisher
from mtpublishers.core import data_from_sql

logging.basicConfig()


def main():
    website_publisher = StaticWebsitePublisher()

    data = data_from_sql()
    data.register_observer(website_publisher)
    data.notify()


if __name__ == '__main__':
    main()
    exit()
