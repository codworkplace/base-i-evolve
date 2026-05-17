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
- **LLM:** gpt-4o-mini (через API vsegpt.ru)
- **Деплой:** Render.com (Docker)

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

### 5. Запустите API

python -m app.main

### 6. Запустите UI (в другом терминале)

streamlit run app/ui.py

**Приложение будет доступно:**

- UI: http://localhost:8501
- API: http://localhost:8000

### 📁 Структура проекта

base-i-evolve/
├── app/
│   ├── main.py           # FastAPI бэкенд
│   ├── ui.py             # Streamlit интерфейс
│   ├── real/             # Реальные реализации (LLM, выбор кейсов)
│   └── stub/             # Заглушки для быстрого прототипирования
├── data/                 # JSON-файлы с ролями, компетенциями, кейсами
├── requirements.txt      # Зависимости Python
└── Dockerfile            # Контейнеризация для деплоя


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

**При пуше в ветку main Render автоматически:**

1. Собирает Docker-образ
2. Деплоит API и UI как отдельные сервисы
3. Применяет переменные окружения

### 📝 Лицензия

MIT

### 👥 Контакты

По вопросам сотрудничества и внедрения: workkm30@gmail.com
