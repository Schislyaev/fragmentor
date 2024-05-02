import argparse
import asyncio

from db.models.booking import Booking  # noqa
from db.models.payment import Payment  # noqa
from db.models.schedule import Schedule  # noqa
from db.models.user import User

# Парсинг аргументов командной строки
parser = argparse.ArgumentParser(description="Create a new superuser")
parser.add_argument("email", type=str, help="Email of the superuser")
parser.add_argument("password", type=str, help="Password of the superuser")

args = parser.parse_args()

# Создание объекта суперпользователя
superuser = {
    'email': args.email,
    'password': args.password,  # Пароль должен хешироваться внутри конструктора модели
    'is_trainer': False,
    'is_superuser': True
}

asyncio.run(User.add(data=superuser))

print(f"Superuser {args.email} created successfully.")
