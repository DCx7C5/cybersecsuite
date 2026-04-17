import sys
import logging
from pathlib import Path
from logging import getLogger, INFO
from logging import handlers
from logging import Formatter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASGI_LOG = PROJECT_ROOT / "asgi.log"

root_logger = getLogger("cybersecsuite")
root_logger.setLevel(INFO)


file_handler = handlers.RotatingFileHandler(
    filename=ASGI_LOG, maxBytes=1024*1024, backupCount=5, encoding='utf-8'
)

stream_handler = logging.StreamHandler(
    stream=sys.stdout
)

formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)
