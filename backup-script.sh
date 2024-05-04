#!/bin/sh
# Скрипт для создания бэкапа базы данных
PGPASSWORD=$POSTGRES_PASSWORD pg_dump -U $POSTGRES_USER -h localhost $POSTGRES_DB > /backups/db-backup-$(date +%Y%m%d-%H%M%S).sql
