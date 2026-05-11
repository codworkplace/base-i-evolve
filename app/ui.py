# app/ui.py
import sys
import io
import os
import streamlit as st
import requests

# Настройка кодировки для Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Определяем API URL в зависимости от окружения
if os.getenv("RENDER"):
    API_URL = os.getenv("API_URL", "https://bs-evolve-api.onrender.com")
else:
    API_URL = "http://localhost:8000"

# Для отладки (в логах Render будет видно)
print(f"[BS-Evolve] Using API_URL: {API_URL}")

st.set_page_config(page_title="BS-Evolve", page_icon="🎯", layout="wide")
st.title("🎯 BS-Evolve — Оценка и развитие компетенций")

# Инициализация сессии
if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.role = None
    st.session_state.role_name = ""
    st.session_state.competencies = []
    st.session_state.diagnostic_scores = {}
    st.session_state.completed_competencies = []
    st.session_state.current_case = None
    st.session_state.current_competency_index = 0
    st.session_state.competencies_to_learn = []
    st.session_state.show_evaluation = False
    st.session_state.evaluation_result = None

# ==================== ШАГ 1: ВЫБОР РОЛИ ====================
if st.session_state.step == 1:
    st.header("Шаг 1: Выберите роль")
    
    try:
        response = requests.get(f"{API_URL}/roles", timeout=10)
        if response.status_code == 200:
            roles = response.json()
            role_names = [r.get("name", r["id"]) for r in roles]
            
            selected_name = st.selectbox("Доступные роли", role_names)
            
            if st.button("Выбрать роль"):
                selected_role = next(r for r in roles if r.get("name", r["id"]) == selected_name)
                st.session_state.role = selected_role["id"]
                st.session_state.role_name = selected_name
                
                # Загружаем компетенции
                role_data = requests.get(f"{API_URL}/roles/{st.session_state.role}").json()
                st.session_state.competencies = role_data.get("competencies", [])
                st.session_state.step = 2
                st.rerun()
        else:
            st.error(f"Ошибка: {response.status_code}")
    except Exception as e:
        st.error(f"Ошибка подключения к API: {e}")
        st.info(f"API URL: {API_URL}")


# ==================== ШАГ 2: ДИАГНОСТИКА ====================
elif st.session_state.step == 2:
    st.header(f"Шаг 2: Диагностический срез для роли '{st.session_state.role_name}'")
    
    st.info("Оцените свой уровень по каждой компетенции (0-100%)")
    
    scores = {}
    cols = st.columns(2)
    for idx, comp in enumerate(st.session_state.competencies):
        with cols[idx % 2]:
            name = comp.get('name', comp['code'])
            score = st.slider(
                f"{comp['code']}: {name}",
                0, 100, 50,
                key=f"diag_{comp['code']}"
            )
            scores[comp['code']] = score
    
    if st.button("Завершить диагностику и начать обучение"):
        st.session_state.diagnostic_scores = scores
        
        # Собираем список компетенций для обучения (балл < 70)
        st.session_state.competencies_to_learn = [
            comp for comp in st.session_state.competencies
            if scores.get(comp['code'], 50) < 70
        ]
        
        if not st.session_state.competencies_to_learn:
            st.session_state.step = 4
        else:
            st.session_state.step = 3
            st.session_state.completed_competencies = []
            st.session_state.current_competency_index = 0
            st.session_state.current_case = None
        
        st.rerun()


# ==================== ШАГ 3: КЕЙСЫ ====================
elif st.session_state.step == 3:
    st.header(f"Шаг 3: Практические кейсы")
    
    # Показываем результат оценки если есть
    if st.session_state.get('show_evaluation', False) and st.session_state.get('evaluation_result'):
        eval_result = st.session_state.evaluation_result
        st.subheader("📊 Результат оценки")
        
        score = eval_result.get('total_score', 0)
        st.metric("Балл", f"{score}%")
        
        if eval_result.get('passed', False):
            st.success("✅ Компетенция зачтена!")
        else:
            st.warning("⚠️ Компетенция не зачтена. Попробуйте другой кейс.")
        
        with st.expander("Подробности оценки"):
            st.write(f"**Feedback:** {eval_result.get('feedback', '')}")
            st.write("**Оценка по критериям:**")
            for result in eval_result.get('results', []):
                verdict_icon = "✅" if result['verdict'] == 'да' else "❌"
                st.write(f"{verdict_icon} **{result['criterion']}**")
                st.caption(f"Evidence: {result.get('evidence', 'Нет пояснения')}")
        
        if st.button("Продолжить"):
            if eval_result.get('passed', False):
                current_comp = st.session_state.competencies_to_learn[st.session_state.current_competency_index]
                st.session_state.completed_competencies.append(current_comp['code'])
                st.session_state.current_competency_index += 1
            st.session_state.current_case = None
            st.session_state.show_evaluation = False
            st.session_state.evaluation_result = None
            st.rerun()
        
        # Если кнопка не нажата — остаемся в этом состоянии
    else:
        # Нормальный поток — показываем текущий кейс
        total = len(st.session_state.competencies_to_learn)
        completed = len(st.session_state.completed_competencies)
        
        if total > 0:
            progress = completed / total
            st.progress(progress)
            st.write(f"**Прогресс:** {completed} из {total} компетенций освоено")
        
        # Если все компетенции пройдены
        if total > 0 and completed >= total:
            st.success("🎉 Поздравляем! Вы успешно освоили все компетенции!")
            if st.button("Показать финальный отчет"):
                st.session_state.step = 4
                st.rerun()
        
        # Если нет компетенций для обучения
        elif total == 0:
            st.info("Все компетенции уже на высоком уровне!")
            if st.button("Перейти к отчету"):
                st.session_state.step = 4
                st.rerun()
        
        # Показываем текущую компетенцию
        elif st.session_state.current_competency_index < len(st.session_state.competencies_to_learn):
            current_comp = st.session_state.competencies_to_learn[st.session_state.current_competency_index]
            comp_code = current_comp['code']
            comp_name = current_comp.get('name', comp_code)
            
            st.subheader(f"Текущая компетенция: {comp_code} - {comp_name}")
            st.write(f"**Ваш текущий уровень:** {st.session_state.diagnostic_scores.get(comp_code, 50)}%")
            st.write(f"**Целевой уровень:** 70% и выше")
            
            # Загружаем кейс
            if st.session_state.current_case is None:
                with st.spinner("Загружаем кейс..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/cases/select",
                            json={
                                "user_id": st.session_state.get("user_id", "test_user"),
                                "competency_id": comp_code,
                                "user_level": st.session_state.diagnostic_scores.get(comp_code, 50) / 100
                            },
                            timeout=30
                        )
                        if response.status_code == 200:
                            st.session_state.current_case = response.json()
                        else:
                            st.error("Не удалось загрузить кейс")
                    except Exception as e:
                        st.error(f"Ошибка: {e}")
            
            # Показываем кейс
            case = st.session_state.current_case
            if case and "error" not in case:
                st.info(f"**{case.get('title', 'Практический кейс')}**")
                st.write(case.get('scenario', ''))
                
                with st.expander("📋 Критерии оценки (чек-лист)"):
                    for item in case.get('checklist', []):
                        st.write(f"- {item}")
                
                answer = st.text_area("**Ваш ответ:**", height=200, key=f"answer_{comp_code}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📤 Отправить на оценку", key=f"submit_{comp_code}"):
                        if not answer.strip():
                            st.warning("Пожалуйста, введите ответ перед отправкой")
                        else:
                            with st.spinner("ИИ оценивает ваш ответ..."):
                                try:
                                    eval_response = requests.post(
                                        f"{API_URL}/cases/evaluate",
                                        json={
                                            "user_id": st.session_state.get("user_id", "test_user"),
                                            "competency_id": comp_code,
                                            "answer": answer
                                        },
                                        timeout=60
                                    )
                                    
                                    if eval_response.status_code == 200:
                                        evaluation = eval_response.json()
                                        st.session_state.evaluation_result = evaluation
                                        st.session_state.show_evaluation = True
                                        st.rerun()
                                    else:
                                        st.error(f"Ошибка: {eval_response.status_code}")
                                except Exception as e:
                                    st.error(f"Ошибка: {e}")
                
                with col2:
                    if st.button("🔄 Другой кейс", key=f"next_{comp_code}"):
                        st.session_state.current_case = None
                        st.rerun()
            else:
                st.error("Нет доступных кейсов для этой компетенции")
                if st.button("Пропустить эту компетенцию"):
                    st.session_state.completed_competencies.append(comp_code)
                    st.session_state.current_competency_index += 1
                    st.session_state.current_case = None
                    st.rerun()


# ==================== ШАГ 4: ФИНАЛЬНЫЙ ОТЧЕТ ====================
elif st.session_state.step == 4:
    st.header("🎉 Результаты обучения")
    
    st.success("Вы успешно завершили программу развития!")
    
    # Расчет итогового PI
    if st.session_state.diagnostic_scores:
        avg_score = sum(st.session_state.diagnostic_scores.values()) / len(st.session_state.diagnostic_scores)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Итоговый PI", f"{avg_score:.1f}%")
        with col2:
            passed_comp = len(st.session_state.completed_competencies)
            total_comp = len(st.session_state.competencies_to_learn) if st.session_state.competencies_to_learn else len(st.session_state.competencies)
            st.metric("Освоено компетенций", f"{passed_comp}/{total_comp}")
        with col3:
            if avg_score >= 70:
                st.metric("Статус", "✅ Сдано")
            else:
                st.metric("Статус", "⚠️ На доработку")
    
    # Таблица результатов
    st.subheader("Детализация по компетенциям")
    
    data = []
    for comp in st.session_state.competencies:
        comp_code = comp['code']
        score = st.session_state.diagnostic_scores.get(comp_code, 0)
        is_completed = comp_code in st.session_state.completed_competencies
        
        if score >= 70:
            status = "✅ Высокий уровень"
        elif is_completed:
            status = "✅ Освоено"
        else:
            status = "🟡 Требуется практика"
        
        data.append({
            "Компетенция": comp_code,
            "Название": comp.get('name', ''),
            "Балл": f"{score}%",
            "Статус": status
        })
    
    st.table(data)
    
    if st.button("Начать заново"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ==================== БОКОВАЯ ПАНЕЛЬ ====================
with st.sidebar:
    st.header("📊 Информация")
    
    if st.session_state.step == 3 and st.session_state.competencies_to_learn:
        current = st.session_state.current_competency_index + 1
        total = len(st.session_state.competencies_to_learn)
        if total > 0 and current <= total:
            st.write(f"**Текущий кейс:** {current}/{total}")
    
    if st.session_state.diagnostic_scores:
        st.write("**Ваши баллы:**")
        for code, score in list(st.session_state.diagnostic_scores.items())[:5]:
            st.write(f"- {code}: {score}%")
    
    if st.button("🔄 Сбросить прогресс"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()