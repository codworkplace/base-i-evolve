import streamlit as st
import requests
import json

# Настройка страницы
st.set_page_config(page_title="BS-Evolve", page_icon="🎯", layout="wide")

st.title("🎯 BS-Evolve — Оценка и развитие компетенций")
st.caption("Версия MVP с заглушками | Режим: Stub")

# Инициализация сессии
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_1"
    st.session_state.role = None
    st.session_state.competencies = []
    st.session_state.diagnostic_passed = False

# Боковая панель
with st.sidebar:
    st.header("📋 Информация")
    st.write(f"Пользователь: {st.session_state.user_id}")
    
    if st.button("🔄 Сбросить прогресс"):
        st.session_state.diagnostic_passed = False
        st.session_state.competencies = []
        st.rerun()

# Основной контент
API_URL = "http://localhost:8000"

# Шаг 1: Выбор роли
if not st.session_state.role:
    st.header("Шаг 1: Выберите роль")
    
    try:
        response = requests.get(f"{API_URL}/roles")
        roles = response.json()
        
        role_options = {role["name"]: role["id"] for role in roles}
        selected_role_name = st.selectbox("Доступные роли", list(role_options.keys()))
        
        if st.button("Выбрать роль"):
            st.session_state.role = role_options[selected_role_name]
            # Загружаем компетенции
            role_data = requests.get(f"{API_URL}/roles/{st.session_state.role}").json()
            st.session_state.competencies = role_data["competencies"]
            st.rerun()
    except Exception as e:
        st.error(f"Ошибка подключения к API: {e}")
        st.info("Убедитесь, что сервер запущен: python app/main.py")

# Шаг 2: Карта компетенций
elif not st.session_state.diagnostic_passed:
    st.header("Шаг 2: Карта компетенций")
    
    st.subheader("Ваши компетенции для оценки")
    
    # Показываем компетенции в виде карточек
    cols = st.columns(3)
    for idx, comp in enumerate(st.session_state.competencies):
        with cols[idx % 3]:
            with st.expander(f"{comp['code']}: {comp['name']}"):
                st.write(f"**Тип:** {comp['type']}")
                st.write(f"**Категория:** {comp['category']}")
                st.write(f"**Описание:** {comp['description']}")
    
    st.info("💡 Диагностический срез поможет определить ваш текущий уровень по этим компетенциям")
    
    if st.button("Начать диагностику"):
        st.session_state.diagnostic_passed = True
        st.rerun()

# Шаг 3: Диагностика (заглушка)
else:
    st.header("Шаг 3: Диагностический срез")
    
    st.success("✅ Вы готовы к диагностике!")
    
    # Простая диагностика-заглушка
    st.subheader("Оцените себя по каждой компетенции")
    
    scores = {}
    for comp in st.session_state.competencies:
        score = st.slider(
            f"{comp['code']} - {comp['name']}",
            0, 100, 50, key=f"slider_{comp['code']}"
        )
        scores[comp['code']] = score
    
    if st.button("Завершить диагностику и получить рекомендации"):
        st.session_state.diagnostic_scores = scores
        
        # Показываем результаты
        st.subheader("📊 Результаты диагностики")
        
        # Определяем средний уровень
        avg_score = sum(scores.values()) / len(scores)
        
        if avg_score < 40:
            level = "🔴 Базовый"
            recommendation = "Рекомендуется пройти полный курс обучения"
        elif avg_score < 70:
            level = "🟡 Средний"
            recommendation = "Требуется практика на кейсах"
        else:
            level = "🟢 Продвинутый"
            recommendation = "Можно переходить к итоговой симуляции"
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Общий уровень", level)
        with col2:
            st.metric("Средний балл", f"{avg_score:.1f}%")
        
        st.write(f"**Рекомендация:** {recommendation}")
        
        # Таблица результатов
        st.subheader("Детализация по компетенциям")
        data = []
        for comp in st.session_state.competencies:
            data.append({
                "Компетенция": comp['code'],
                "Название": comp['name'],
                "Балл": scores[comp['code']],
                "Уровень": "🟢 Высокий" if scores[comp['code']] >= 70 else "🟡 Средний" if scores[comp['code']] >= 40 else "🔴 Низкий"
            })
        
        st.dataframe(data, use_container_width=True)
        
        st.info("ℹ️ В следующей версии здесь будут кейсы для практики и реальная оценка через AI")
        
        st.balloons()
        
        if st.button("Начать сначала"):
            for key in ["role", "competencies", "diagnostic_passed", "diagnostic_scores"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()