# BS-Evolve

Платформа оценки и развития профессиональных компетенций сотрудников через ролевую модель, KPI, карту компетенций и ИИ-оценку кейсов.

## 🚀 Деплой (Production)

- **Веб-интерфейс:** [https://base-i-evolve-ui.onrender.com](https://base-i-evolve-ui.onrender.com)
- **API:** [https://base-i-evolve-api.onrender.com](https://base-i-evolve-api.onrender.com)

## ✨ Возможности MVP

- ✅ Выбор роли (Менеджер отдела продаж)
- ✅ Карта компетенций (7 ключевых навыков: SLS-04, SLS-07, SLS-10, SLS-14, SLS-15, FIN-08, CRM-03)
- ✅ Диагностический срез (оценка текущего уровня 0-100%)
- ✅ Практические кейсы с ИИ-оценкой (через vsegpt.ru, модель gpt-4o-mini)
- ✅ Skill State Engine (отслеживание прогресса)
- ✅ Итоговый отчет с PI (Professional Index)

## 🛠 Технологии

- **Backend:** FastAPI (Python)
- **Frontend:** Streamlit
- **База данных:** PostgreSQL (через SQLAlchemy + Alembic)
- **Логирование:** structlog (JSON-формат в продакшене)
- **Тестирование:** pytest, pytest-asyncio, интеграционные тесты, unit-тесты (с моками для LLM)
- **LLM:** gpt-4o-mini (через API vsegpt.ru)
- **Деплой:** Render.com (Docker)
- **CI/CD:** GitHub Actions (lint, test, build)

## 🏁 Запуск для разработки

### 1. Клонируйте репозиторий

git clone https://github.com/codworkplace/base-i-evolve.git  
cd base-i-evolve  

### 2. Создайте виртуальное окружение

python -m venv venv  
source venv/bin/activate  # Linux/Mac  
venv\Scripts\activate     # Windows  

### 3. Установите зависимости

pip install -r requirements.txt

### 4. Настройте переменные окружения

**Создайте файл .env:**

OPENAI_API_KEY=ваш_ключ_vsegpt  
OPENAI_BASE_URL=https://api.vsegpt.ru/v1  
OPENAI_MODEL=openai/gpt-4o-mini  
DATABASE_URL=postgresql://bsuser:bspassword@localhost:5432/bsevolve  
ENVIRONMENT=development  

### 5. Запустите PostgreSQL (через Docker)

docker-compose up -d

**Убедитесь, что контейнеры здоровы:**

docker-compose ps

**Ожидаемый результат: оба контейнера в статусе Up/healthy**

### 6. Примените миграции

alembic upgrade head

### 7. Запустите API

python -m app.main

### 8. Запустите UI (в другом терминале)

streamlit run app/ui.py

**Приложение будет доступно:**

- UI: http://localhost:8501
- API: http://localhost:8000
- Swagger документация API: http://localhost:8000/docs
- ReDoc документация API: http://localhost:8000/redoc

### 🧪 Тестирование

**Все тесты (unit + интеграционные)**

pytest tests/ -v

**Только unit-тесты (быстрые, не требуют БД)**

pytest tests/unit/ -v

**Только интеграционные тесты (требуют запущенный PostgreSQL)**

pytest tests/integration/ -v

**С покрытием кода**

pytest tests/ -v --cov=app

### 📁 Структура проекта

base-i-evolve/  
├── app/  
│   ├── main.py               # FastAPI бэкенд  
│   ├── ui.py                 # Streamlit интерфейс  
│   ├── core/                 # Логирование и конфигурация  
│   ├── db/                   # Модели, миграции (Alembic)  
│   ├── services/             # Бизнес-логика (UserService и др.)  
│   ├── real/                 # Реальные реализации (LLM, выбор кейсов)  
│   └── stub/                 # Заглушки для быстрого прототипирования  
├── data/                     # JSON-файлы с ролями, компетенциями, кейсами  
├── tests/                    # Unit и интеграционные тесты  
├── requirements.txt          # Зависимости Python  
├── docker-compose.yml        # PostgreSQL + pgAdmin  
├── Dockerfile                # Контейнеризация для деплоя  
└── alembic/                  # Миграции базы данных  


### 🧠 Модель оценки

**Оценка ответов на кейсы происходит по чек-листу через LLM:**

- Понимание сути компетенции
- Логика решения
- Применение в кейсе
- Попадание в нужный архетип

**Проходной балл: 70%**

### 📊 Professional Index (PI)

**Рассчитывается как комбинация:**

- Соответствие роли по компетенциям
- Стабильность результатов
- Перенос навыков в кейсы

### 🔄 CI/CD

**При пуше в ветку main GitHub Actions:**

1. Запускает линтеры (ruff, black)
2. Запускает тесты с PostgreSQL (с явным ожиданием готовности БД)
3. Собирает Docker-образ

**Render автоматически деплоит новую версию:**

1. Получает обновлённый код из ветки main
2. Устанавливает зависимости
3. Запускает приложение

### ⚠️ Примечание для разработчиков на Windows

asyncpg (асинхронный драйвер PostgreSQL) работает на Windows нестабильно. Рекомендуется использовать WSL2 или перейти на Linux для локальной разработки. На сервере (Render) используется Linux, поэтому проблем не возникает.

### 📝 Лицензия

MIT

### 👥 Контакты

По вопросам сотрудничества и внедрения: workkm30@gmail.com
