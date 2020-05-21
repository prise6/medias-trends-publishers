from abc import ABC, abstractmethod
import argparse
import sys
import logging
import mtpublishers.tools.config as cfg
from mtpublishers import config
from mtpublishers.tasks import publish

logger = logging.getLogger(__name__)
logging.basicConfig(level="DEBUG")


def _argument_config_file(parser):
    parser.add_argument("-f", "--config-dir", help="Configuration directory. Load mediastrends.MODE.ini", type=str)


def _argument_mode(parser):
    parser.add_argument("-m", "--mode", help="Mode. Override MEDIASTRENDS_MODE environment", type=str)


def _argument_publishers(parser):
    parser.add_argument("-p", "--publishers", help="Which publishers must publish data", type=str, nargs="+", choices=["website"])


def _argument_force(parser):
    parser.add_argument("-f", "--force", help="Force publish even if data doesn't change", action="store_true")


def _argument_test(parser):
    parser.add_argument("--test", help="Action is not really called", action='store_true')


class AbstractParser(ABC):

    def __init__(self, parser=None):
        if parser is None:
            parser = argparse.ArgumentParser()
        self.parser = parser
        self.build()
        self.parsed_args_dict = {}
        self.parser.set_defaults(func=self.task)

    def build(self):
        return

    def task(self, **kwargs):
        raise NotImplementedError("This parser does not handle these arguments")

    def execute(self, args=sys.argv[1:]):
        parsed_args = self.parser.parse_args(args)
        self.parsed_args_dict = vars(parsed_args)

        parsed_args.func(**self.parsed_args_dict)


class AbstractSubParsers(ABC):

    def __init__(self, parent_parser, **kwargs):
        self.parent_parser = parent_parser
        self.subparsers = self.parent_parser.add_subparsers(**kwargs)
        self.add_parsers()

    @abstractmethod
    def add_parsers(self):
        return


class PublishParser(AbstractParser):

    def build(self):
        _argument_publishers(self.parser)
        _argument_force(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        publish(**kwargs)


class MTPublishersCLI(AbstractParser):

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog='mediastrends',
            description="CLI to make publishing easier. Data come from medias trends data.",
            formatter_class=argparse.RawTextHelpFormatter
        )
        super().__init__(parser)

    def build(self):
        TopLevelSubParsers(self.parser, title="Top level commands")
        _argument_config_file(self.parser)
        _argument_mode(self.parser)

    def execute(self, args=sys.argv[1:]):
        parsed_args = self.parser.parse_args(args)
        parsed_args_dict = vars(parsed_args)

        config_dir = parsed_args_dict.get('config_dir', None)
        mode = parsed_args_dict.get('mode', None)
        if config_dir or mode:
            cfg.populate_config(config=config, user_dir_config=config_dir, mode=mode, reload_=True)

        super().execute(args)


class TopLevelSubParsers(AbstractSubParsers):

    def add_parsers(self):
        PublishParser(self.subparsers.add_parser("publish", help="Publish medias trends"))


def main():
    cli = MTPublishersCLI()
    try:
        cli.execute()
    except NotImplementedError as err:
        logger.debug(err)
        cli.parser.print_help()


if __name__ == '__main__':
    main()
    exit()
