import streamlit as st
import requests

# ========== НАСТРОЙКА ==========
# Для локальной разработки используйте localhost, для продакшена - адрес Render
# API_URL = "http://localhost:8000"          # локальный API
API_URL = "https://base-i-evolve-api.onrender.com"   # продакшен (раскомментировать при деплое)

# ========== УПРАВЛЕНИЕ СЕССИЕЙ ==========
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user" not in st.session_state:
    st.session_state.user = None

# ========== СТРАНИЦА ЛОГИНА ==========
if not st.session_state.access_token:
    st.title("Авторизация")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Войти")
        if submitted:
            resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.access_token = data["access_token"]
                # Получение данных пользователя
                me = requests.get(f"{API_URL}/users/me", headers={"Authorization": f"Bearer {data['access_token']}"})
                if me.status_code == 200:
                    st.session_state.user = me.json()
                    st.rerun()
                else:
                    st.error("Не удалось получить данные пользователя. Проверьте токен.")
                    st.session_state.access_token = None
            else:
                st.error(f"Ошибка входа: {resp.status_code} - {resp.text}")
    st.stop()

# ========== БОКОВАЯ ПАНЕЛЬ (ОБЩАЯ) ==========
st.sidebar.write(f"👤 Добро пожаловать, {st.session_state.user.get('email')}")
if st.sidebar.button("🚪 Выйти"):
    st.session_state.access_token = None
    st.session_state.user = None
    st.rerun()

# ========== ОСНОВНОЙ КОНТЕНТ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==========
st.header("Основной функционал")
st.write("Здесь будет интерфейс для выбора роли, диагностики и кейсов.")
# TODO: Перенести сюда существующий код (выбор роли, кейсы, оценка)

# ========== АДМИН-ПАНЕЛЬ (ТОЛЬКО ДЛЯ ADMIN) ==========
if st.session_state.user and st.session_state.user.get("auth_role") == "admin":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔐 Администрирование")
    admin_page = st.sidebar.radio("Управление", ["Пользователи", "Кейсы", "Компетенции"])

    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

    # ----- Управление пользователями -----
    if admin_page == "Пользователи":
        st.header("👥 Пользователи")
        resp = requests.get(f"{API_URL}/admin/users", headers=headers)
        if resp.status_code == 200:
            users = resp.json()
            for u in users:
                cols = st.columns([3, 2, 2, 1])
                cols[0].write(u["email"])
                cols[1].write(u["auth_role"])
                cols[2].write(u["role_id"])
                if cols[3].button("Изменить роль", key=f"role_{u['id']}"):
                    new_role = st.selectbox("Новая роль", ["user", "manager", "admin"], key=f"select_{u['id']}")
                    if st.button("Сохранить", key=f"save_{u['id']}"):
                        put_resp = requests.put(
                            f"{API_URL}/admin/users/{u['id']}/role",
                            json={"role": new_role},
                            headers=headers
                        )
                        if put_resp.status_code == 200:
                            st.success("Роль обновлена")
                            st.rerun()
                        else:
                            st.error("Ошибка обновления")
        else:
            st.error("Не удалось загрузить пользователей")

    # ----- Управление кейсами -----
    elif admin_page == "Кейсы":
        st.header("📚 Управление кейсами")
        resp = requests.get(f"{API_URL}/admin/cases", headers=headers)
        if resp.status_code == 200:
            cases = resp.json()
            for comp_id, case_list in cases.items():
                st.subheader(f"Компетенция {comp_id}")
                for case in case_list:
                    with st.expander(f"{case['title']} (сложность: {case['difficulty']})"):
                        st.write("**Сценарий:**", case["scenario"])
                        st.write("**Чек-лист:**", case["checklist"])
                        if st.button("🗑️ Удалить", key=f"del_{case['id']}"):
                            # Здесь можно вызвать DELETE запрос, если он реализован в API
                            st.warning("Удаление кейсов через UI пока не реализовано.")
            # Форма добавления нового кейса
            with st.form("new_case"):
                st.subheader("➕ Добавить новый кейс")
                new_comp_id = st.text_input("Компетенция (например, SLS-04)")
                new_title = st.text_input("Название")
                new_difficulty = st.selectbox("Сложность", ["easy", "medium", "hard"])
                new_scenario = st.text_area("Сценарий")
                new_checklist = st.text_area("Чек-лист (каждый пункт с новой строки)")
                if st.form_submit_button("Создать"):
                    if not new_comp_id or not new_title or not new_scenario:
                        st.error("Заполните все обязательные поля (компетенция, название, сценарий).")
                    else:
                        checklist_items = [item.strip() for item in new_checklist.split("\n") if item.strip()]
                        payload = {
                            "competency_id": new_comp_id,
                            "title": new_title,
                            "difficulty": new_difficulty,
                            "scenario": new_scenario,
                            "checklist": checklist_items
                        }
                        post_resp = requests.post(f"{API_URL}/admin/cases", json=payload, headers=headers)
                        if post_resp.status_code == 200:
                            st.success("Кейс добавлен")
                            st.rerun()
                        else:
                            st.error(f"Ошибка добавления: {post_resp.text}")
        else:
            st.error("Не удалось загрузить кейсы")

    # ----- Управление компетенциями -----
    elif admin_page == "Компетенции":
        st.header("📋 Управление компетенциями")
        st.info("Функция управления компетенциями будет добавлена позже.")

# ========== ПРИМЕЧАНИЕ ==========
# Если вы хотите использовать продакшен-API, измените API_URL выше на Render-адрес.
