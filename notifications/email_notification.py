import asyncio
import hashlib
from email.mime.text import MIMEText
from uuid import UUID

import aiosmtplib
import httpx
from pydantic import ValidationError

from core.settings import settings
from db.redis import get_redis
from server.api.schemas.helpers import ValidateEmail

redis = get_redis()


class EmailSender:
    def __init__(self):
        self.smtp_server = settings.email_smtp_server
        self.port = settings.email_port
        self.sender_email = settings.email_account
        self.redis = redis
        self.password = settings.email_password.get_secret_value()

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
    async def _send(self, message_id: int | UUID, subject: str, message: str, destinations: list):
        try:
            [ValidateEmail(email=destination) for destination in destinations]
        except ValidationError:
            raise ValidationError('Invalid email address')
        try:
            async with aiosmtplib.SMTP(
                    hostname=self.smtp_server,
                    port=self.port,
                    # use_tls=True,
                    # tls_context=ssl.create_default_context()
            ) as server:
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
            print(e)
            return 'ERROR'

    @check_redis
    async def send(self, message_id: int | UUID, subject: str, message: str, destinations: list):
        url = 'https://api.brevo.com/v3/smtp/email'
        payload = {
            'sender': {'name': 'FragMentor', 'email': f'{self.sender_email}'},
            'to': [{'email': f'{destination}'} for destination in destinations],
            'subject': subject,
            'textContent': message
        }

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'api-key': settings.email_api_key,
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, read=30.0)) as client:
            try:
                response = await client.post(
                    url=url,
                    headers=headers,
                    json=payload
                )
                return response.status_code
            except Exception as e:
                raise e


def get_email_service() -> EmailSender:
    return EmailSender()


if __name__ == '__main__':
    email_service = get_email_service()
    asyncio.run(email_service.send(
        message_id=1,
        subject='subj',
        message='test message',
        destinations=['pschhhh@gmail.com']
    ))
