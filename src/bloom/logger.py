import logging
from bloom.config import settings

logger = logging.getLogger("bloom")
formatter = logging.Formatter(
    settings.logging_format,
    datefmt="%H:%M:%S",
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(level=settings.logging_level)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
