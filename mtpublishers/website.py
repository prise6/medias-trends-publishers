import os
import logging
import jinja2
import random
from mtpublishers.core import Publisher
from mtpublishers import config

logger = logging.getLogger(__name__)


class StaticWebsitePublisher(Publisher):

    _TEMPLATE_NAME = {'movies': 'index', 'series': 'series'}

    def __init__(self, jinja_env: jinja2.Environment = None):
        super().__init__()
        self._jinja_env = jinja_env if jinja_env else jinja2.Environment(loader=jinja2.FileSystemLoader(config.get('directory', 'jinja')))
        self._template = None
        self._output = None

    @property
    def output(self):
        return self._output

    def random_content(self, key: str):
        random_content_values = {
            'nav_item_actual': ['fresh', 'recent', 'actual', '2019 and +', 'what about a recent movie?'],
            'nav_item_old': ['2018 and older', 'old', 'wanna see an old movie'],
            'subtitle': [
                'what people are watching lately',
                'you will find what you\'re looking for',
                'one more website to find movies',
                'a great lockdown project'
            ]
        }
        return random.choice(random_content_values.get(key))

    def publish(self):
        try:
            for cat_name, cat_items in self.data.category_items.items():
                template_name = self._TEMPLATE_NAME[cat_name]
                self.load_template(template_name)
                self.render({
                    'items': cat_items.items,
                    'infos': self.data.informations,
                    'nav_item_actual': self.random_content('nav_item_actual'),
                    'nav_item_old': self.random_content('nav_item_old'),
                    'subtitle': self.random_content('subtitle'),
                    'max_valid_date': max([i.get('valid_date') for i in cat_items.items])
                })
                self.dump(template_name)
        except Exception as err:
            logger.error("Error while publishing one page website: %s" % str(err))

    def load_template(self, template_name: str):
        self._template = self._jinja_env.get_template("%s.html" % template_name)

    def render(self, vars: dict):
        self._output = self._template.render(vars)

    def dump(self, template_name: str):
        html_file = os.path.join(config.get('directory', 'website'), '%s.html' % template_name)
        with open(html_file, 'w') as website:
            website.write(self._output)
