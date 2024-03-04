import logging

logger = logging.getLogger("bloom")
formatter = logging.Formatter(
    "[%(name)s %(levelname)s @ %(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(level="INFO")
