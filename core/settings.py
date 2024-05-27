import pathlib

from pydantic import Extra, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # base service urls
    host: str = '127.0.0.1'
    port: int = 8080
    front_port: int = 3000
    front_host: str = ''
    discord_host: str = '127.0.0.1'

    # tg config
    tg_token: str = ''
    tg_admin_id: int = 0

    # discord_bot config
    discord_token: str = ''
    discord_web_server_url: str = ''
    discord_guild_id: int = 0

    # google email notification
    google_email_password: SecretStr = ''

    # email service notification
    email_account: str = ''
    email_password: SecretStr = ''
    email_port: int = 0
    email_smtp_server: str = ''
    email_api_key: str = ''

    # postgres config
    database_url: str = ''
    database_url_trigger: str = ''
    alembic_url: str = ''
    db_user: str = ''
    db_password: str = ''
    db_host: str = ''
    db_port: int = 0
    db_name: str = ''

    # redis config
    redis_host: str = ''
    redis_port: str = ''
    redis_cash_timeout: int = 60 * 5

    # elastic config
    elastic_host: str = ''
    elastic_port: int = 9200

    # security
    secret_key: str = ''
    algorithm: str = ''
    access_token_expire_minutes: int = 360

    # API path
    url: str = '127.0.0.1'
    port: int = 8080

    # YooKassa
    yookassa_secret_key: SecretStr = ''
    yookassa_shop_id: SecretStr = ''
    yookassa_return_url: str = 'https://fac4-45-230-12-225.ngrok-free.app'

    # CryptoCould
    cryptocloud_api_key: SecretStr = ''
    cryptocloud_shop_id: SecretStr = ''

    # reCaptchaV3
    google_recaptcha_key: SecretStr = ''

    # Google OAuth2
    google_client_id: SecretStr = ''
    google_client_secret: SecretStr = ''

    template_dir: str = ''

    debug: int = 1

    project_root_path: str = str(pathlib.Path(__file__).parent.parent)

    class Config:
        env_file = f'{str(pathlib.Path(__file__).parent.parent)}/.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = Extra.allow


settings = Settings()
