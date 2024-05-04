FROM postgres:14-alpine

# Установка cron и создание папки для скриптов
RUN apk add --no-cache dcron && \
    mkdir -p /backups && \
    mkdir -p /etc/scripts

# Добавление скрипта бэкапа
COPY backup-script.sh /etc/scripts/backup-script.sh
RUN chmod +x /etc/scripts/backup-script.sh

# Настройка cron задачи
RUN echo "0 2 * * * /etc/scripts/backup-script.sh" > /etc/crontabs/root

# Команда для запуска cron в фоне и PostgreSQL на переднем плане
CMD ["sh", "-c", "crond && docker-entrypoint.sh postgres"]
