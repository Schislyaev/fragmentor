import hashlib

import aiosmtplib
from email.mime.text import MIMEText
from pydantic import ValidationError
from core.settings import settings
from server.api.schemas.helpers import ValidateEmail
from db.redis import get_redis
from uuid import UUID

redis = get_redis()


class EmailSender:
    def __init__(self):
        self.smtp_server = 'smtp.gmail.com'
        self.port = 465
        self.sender_email = 'pschhhh@gmail.com'
        self.redis = redis
        self.password = settings.google_email_password.get_secret_value()

    @staticmethod
    def check_redis(func):
        async def wrapper(self, message_id, subject, message, destinations):
            # Проверяем, существует ли такой ключ в Redis асинхронно
            message_id = hashlib.md5((str(message_id) + subject).encode()).hexdigest()
            if await self.redis.exists(message_id):
                print('Message already sent')
                return 'Message already sent'
            else:
                # Если сообщение не было отправлено, вызываем функцию отправки
                result = await func(self, message_id, subject, message, destinations)
                # Если отправка прошла успешно, сохраняем идентификатор в Redis
                if result == 'OK':
                    await self.redis.set(message_id, 'sent')
                return result
        return wrapper

    @check_redis
    async def send(self, message_id: int | UUID, subject: str, message: str, destinations: list):
        try:
            [ValidateEmail(email=destination) for destination in destinations]
        except ValidationError:
            raise ValidationError('Invalid email address')
        try:
            async with aiosmtplib.SMTP(hostname=self.smtp_server, port=self.port, use_tls=True) as server:
                await server.login(self.sender_email, self.password)
                msg = MIMEText(message, 'plain', 'utf-8')
                msg['Subject'] = subject
                [await server.sendmail(
                    self.sender_email,
                    destination,
                    msg.as_string()
                ) for destination in destinations]
            return 'OK'
        except Exception as e:
            return 'ERROR'


def get_email_service() -> EmailSender:
    return EmailSender()


if __name__ == '__main__':
    email_service = get_email_service()
    email_service.send('test message')
