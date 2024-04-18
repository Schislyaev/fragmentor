from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime

from db.postgres import async_session


async def update_table(cls, field, data):
    data['updated_at'] = datetime.now()
    async with async_session() as session:
        async with session.begin():
            try:
                # Найти объект по ID
                obj = await session.get(cls, field)
                if not obj:
                    raise HTTPException(status_code=404, detail="Object not found")

                # Обновление атрибутов объекта новыми значениями из data
                for key, value in data.items():
                    setattr(obj, key, value)

                # session.add(obj) # В данном контексте не обязательно, так как изменения отслеживаются
                await session.commit()
                return obj  # Возвращаем обновленный объект
            except IntegrityError:
                await session.rollback()
                # raise IntegrityError(orig=)
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Violation of unique constraints")

            except SQLAlchemyError as e:
                await session.rollback()
                # logger.exception(e)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_item(cls, cls_field, cls_filter):

    async with async_session() as session:
        try:
            # Построение запроса для выборки пользователя по email
            stmt = select(cls).filter(cls_field == cls_filter)

            # Выполнение запроса и получение результата
            result = await session.execute(stmt)
            return result.scalars().first()  # Получить первую запись

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "Error"})



