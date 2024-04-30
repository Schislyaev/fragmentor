from passlib.context import CryptContext
from uuid import UUID
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def encode_id_to_uuid_style(original_id: str) -> UUID:
    """ Функция конвертации id Криптоклауд в UUID """

    # Конвертируем каждый символ в двухзначный hex код
    encoded_hex = ''.join([f"{ord(c):02x}" for c in original_id])

    # Дополняем результат до 32 символов (стандартный размер UUID без '-')
    encoded_hex = encoded_hex.ljust(32, '0')

    # Форматируем как UUID
    return UUID(
        f"{encoded_hex[:8]}-{encoded_hex[8:12]}-{encoded_hex[12:16]}-{encoded_hex[16:20]}-{encoded_hex[20:32]}"
    )


def decode_uuid_style_to_id(encoded_uuid: UUID) -> str:
    encoded_uuid = str(encoded_uuid)
    # Убираем дефисы и отсекаем лишнее
    clean_hex = encoded_uuid.replace('-', '')[:16]  # Оригинальный ID занимает первые 16 символов hex

    # Преобразуем hex обратно в ASCII
    chars = [chr(int(clean_hex[i:i + 2], 16)) for i in range(0, len(clean_hex), 2)]
    return ''.join(chars)


def generate_random_string(length):
    """
    Генерирует случайную строку указанной длины.

    :param length: Int - длина случайной строки.
    :return: Str - случайная строка указанной длины.
    """
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    result = ''.join(random.choice(characters) for _ in range(length))
    return result
