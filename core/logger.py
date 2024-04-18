import logging
from datetime import datetime

from core.settings import settings


def log(name):
    file_name = f"{str(datetime.today()).split(' ')[0]}.log"
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(f"{settings.project_root_path}/logs/{file_name}", mode='a', encoding='utf-8')
    formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
