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
