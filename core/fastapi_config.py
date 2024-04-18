import logging
import pathlib

from pydantic import Extra
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    project_name: str = 'FragHub'
    project_description: str = 'Ultimate E-Fighting Training Hub'
    project_version: str = '1.0.0'
    log_level: int = logging.DEBUG

    # @property
    # def elastic_connection_string(self):
    #     return f'{config.elastic_host}:{config.elastic_port}'

    class Config:
        env_file = f'{str(pathlib.Path(__file__).parent.parent)}/.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = Extra.allow


config = AppConfig()
