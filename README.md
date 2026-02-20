# ExampleGame - Game Server Template

Шаблон игрового сервера для Telegram Mini Apps с поддержкой:
- FastAPI backend
- PostgreSQL для хранения данных
- ClickHouse для аналитики
- Metabase для визуализации
- Telegram Bot API интеграция
- Система энергии

## 🚀 Быстрый старт

### 1. Копирование и настройка

```bash
# Скопируйте папку ExampleGame в новый проект
cp -r ExampleGame MyNewGame
cd MyNewGame

# Создайте файл с секретами
cp backend/.env.secret.example backend/.env.secret

# Отредактируйте переменные окружения
nano .env
nano backend/.env.secret
```

### 2. Настройка переменных окружения

В файле `.env`:
```env
# Название игры (используется в логах, API и БД)
GAME_NAME=MyNewGame
GAME_PREFIX=mng

# Порты (измените если конфликтуют с другими сервисами)
BACKEND_PORT=8002
POSTGRES_PORT=5433
CLICKHOUSE_HTTP_PORT=8123
METABASE_PORT=3000
```

В файле `backend/.env.secret`:
```env
# Telegram Bot Token
TG_BOT_TOKEN=your_bot_token_here

# JWT секрет (сгенерируйте случайную строку)
SECRET_KEY__JWT=your_random_secret_key_here
```

### 3. Запуск

```bash
# Инициализация (первый запуск)
make init

# Запуск всех сервисов
make run

# Проверка логов
make logs
```

### 4. Проверка работоспособности

- **API документация (Swagger):** http://localhost:8002/docs
- **Health check:** http://localhost:8002/health
- **Metabase:** http://localhost:3000

## 📁 Структура проекта

```
ExampleGame/
├── Makefile                # Команды управления
├── docker-compose.yml      # Docker сервисы
├── .env                    # Переменные окружения
│
├── backend/                # FastAPI приложение
│   ├── app/
│   │   ├── main.py        # Точка входа
│   │   ├── config.py      # Конфигурация
│   │   ├── users/         # Модуль пользователей
│   │   ├── energy/        # Система энергии
│   │   ├── tg/            # Telegram интеграция
│   │   ├── payments/      # Платежи
│   │   ├── game/          # Игровая логика (расширяйте)
│   │   └── analytics/     # ClickHouse аналитика
│   └── db_migrations/     # Миграции БД
│
├── apache2/               # Apache конфигурация
├── clickhouse/            # ClickHouse настройки
└── systemd/               # Systemd сервисы
```

## 🔧 Команды Makefile

```bash
# Основные команды
make init           # Инициализация проекта
make run            # Запуск всех сервисов
make down           # Остановка сервисов
make logs           # Просмотр логов

# Backend
make backend/migrate        # Применить миграции
make backend/gen_migration  # Создать новую миграцию
make backend/bash           # Войти в контейнер
make backend/test           # Запустить тесты

# Качество кода
make backend/lint           # Проверка линтером
make backend/lint-fix       # Автоисправление
make backend/typecheck      # Проверка типов

# Docker
make clean                  # Очистка Docker ресурсов
make clean-all              # Полная очистка

# ClickHouse
make ch/status              # Статус таблиц
make ch/migrate             # Применить миграции
```

## 🎮 API Endpoints

### Пользователи
- `POST /{prefix}/login` - Авторизация через Telegram
- `GET /{prefix}/user` - Данные пользователя

### Энергия
- `GET /{prefix}/energy` - Текущая энергия
- `POST /{prefix}/energy/spend` - Потратить энергию

### Игра (пример)
- `POST /{prefix}/game/action` - Игровое действие

### Telegram
- `POST /telegram/webhook` - Webhook для бота

## 🔐 Безопасность

- Все секреты хранятся в `backend/.env.secret`
- Telegram initData валидируется с использованием HMAC
- JWT токены для сессий (опционально)

## 🚀 Деплой на сервер

1. Скопируйте проект на сервер
2. Настройте SSL сертификаты
3. Отредактируйте `apache2/example.conf`
4. Запустите `apache2/setup-apache-proxy.sh`
5. Настройте systemd сервис

## 📊 Аналитика

Проект использует ClickHouse для сбора аналитики:
- События пользователей
- Платежи
- Сессии
- Воронки

Просмотр через Metabase: http://localhost:3000

## 🤝 Расширение

Для добавления новой игровой логики:

1. Создайте новый модуль в `backend/app/`
2. Добавьте роутер в `backend/app/main.py`
3. Создайте миграцию если нужна новая таблица
