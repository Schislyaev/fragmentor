#!/bin/sh
export PGPASSWORD=$POSTGRES_PASSWORD

# Получение текущего года и месяца для создания директорий
YEAR=$(date +%Y)
MONTH=$(date +%b) # Использует короткое имя месяца, например "May"
DAY=$(date +%d)
TIME=$(date +%H-%M)

# Проверка и создание необходимых директорий
BACKUP_PATH="/backups/$YEAR/$MONTH"
mkdir -p $BACKUP_PATH

# Создание бэкапа
pg_dump -h postgres -U $POSTGRES_USER $POSTGRES_DB > ${BACKUP_PATH}/${DAY}_${TIME}_backup.sql

# Удаление файлов бэкапов старше 30 дней
#find /backups -type f -name '*.sql' -mtime +30 -exec rm {} \;
