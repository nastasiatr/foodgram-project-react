Дипломный проект курса Backend python-разработчик от Яндекс.Практикум.

# Проект «Продуктовый помощник» - Foodgram
### Foodgram - Продуктовый помощник. 
Сервис позволяет публиковать рецепты, подписывать на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать сводный список продуктов, рекомендуемых для приготовления одного или нескольких выбранных блюд.

## Технологический стек


## Рабочий процесс.
- build_and_push_to_docker_hub — Сборка и доставка докер-образов на Docker Hub
- deploy - Автоматический деплой проекта на боевой сервер. Выполняется объем файлов из репозитория на сервере:
- send_message - Отправка терминала в Telegram В репозитории на Гитхабе добавляются данные в Settings - Secrets - Actions secrets:
- DOCKER_USERNAME- имя пользователя в DockerHub
- DOCKER_PASSWORD- пароль пользователя в DockerHub.
- HOST- адрес сервера
- USER- пользователь
- SSH_KEY- приватный ssh ключ
- PASSPHRASE- кодовая фраза для ssh-ключа
- DB_ENGINE- django.db.backends.postgresql
- DB_NAME- постгрес (по умолчанию)
- POSTGRES_USER- постгрес (по умолчанию)
- POSTGRES_PASSWORD- постгрес (по умолчанию)
- DB_HOST- db
- DB_PORT- 5432
- SECRET_KEY- секретный ключ приложения django
- ALLOWED_HOSTS- список разрешенных адресов
- TELEGRAM_TO- id своего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
- TELEGRAM_TOKEN- токен Бота (получить токен можно у @BotFather, /token, имя бота)
