from xylogger import BaseLogger


config = None

logger = BaseLogger(
    level=config.get('logging_level', 'debug'),
    release_enable=config.get('logging_release', False)).Logger
logger.write = logger.info
