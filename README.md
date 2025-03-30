# Audio Uploader Service

Сервис для загрузки аудио-файлов с авторизацией через Яндекс и хранением данных в PostgreSQL.

---

## 📦 Стек

- Python 3.12
- FastAPI
- SQLAlchemy (async)
- PostgreSQL 16
- Docker + Docker Compose
- OAuth2 Yandex

---

## 🚀 Запуск проекта через Docker

### 1. Клонировать репозиторий

```bash
  git clone https://github.com/Stanis4live/AudioUploader.git
```

### 2. Перейти в директорию с проектом
```bash
  cd AudioUploader
```

### 3. Создать файл с настройками переменных окружения
```bash
  cp .env.sample .env
```
### 4. Задать настройки в файле .env

### 5. Запустить контейнеры
```bash
  docker-compose up -d --build
```
