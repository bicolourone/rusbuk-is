"""
Главный интерфейс информационной системы
Сайт: Rusbuk.ru (букинистический магазин)
Модули 2, 4, 5, 6
"""

import streamlit as st
import pandas as pd
from modules.database import init_db, get_all_books, search_books, get_stats, clear_db
from modules.parser import run_parser

st.set_page_config(
    page_title="ИС Парсер Rusbuk.ru",
    page_icon="📚",
    layout="wide"
)

init_db()

st.title("📚 Информационная система — Rusbuk.ru")
st.caption("Извлечение данных о книгах с букинистического сайта → база данных → вывод по запросу")

# ====================== БОКОВАЯ ПАНЕЛЬ ======================
with st.sidebar:
    st.header("⚙️ Управление")

    st.subheader("Модуль 1–3: Парсер")
    max_pages = st.slider("Сколько разделов каталога парсить", 1, 4, 2)

    if st.button("🚀 Запустить парсинг", type="primary", use_container_width=True):
        with st.spinner("Парсим Rusbuk.ru..."):
            result = run_parser(max_pages=max_pages)
        if result.get("is_demo"):
            st.warning(result["message"] + " (демо-данные)")
        else:
            st.success(result["message"])
        st.rerun()

    st.divider()

    st.subheader("Статистика базы")
    stats = get_stats()
    st.metric("Всего книг", stats["total_books"])
    st.metric("Уникальных авторов", stats["unique_authors"])
    st.metric("Категорий", stats["categories"])

    st.divider()

    if st.button("🗑️ Очистить базу", use_container_width=True):
        clear_db()
        st.warning("База очищена")
        st.rerun()

    st.divider()
    st.markdown("**Целевой сайт:** [rusbuk.ru](https://rusbuk.ru)")

# ====================== ОСНОВНАЯ ЧАСТЬ ======================
tab1, tab2 = st.tabs(["📋 Все книги", "🔍 Поиск"])

with tab1:
    st.subheader("Модуль 4–6: Вывод информации из базы")

    books = get_all_books()

    if not books:
        st.info("База пустая. Нажмите «Запустить парсинг» слева →")
    else:
        df = pd.DataFrame(books)
        df_display = df.rename(columns={
            "id": "ID",
            "title": "Название",
            "author": "Автор",
            "price": "Цена",
            "category": "Категория",
            "url": "Ссылка",
            "source": "Источник",
            "created_at": "Добавлено"
        })

        st.dataframe(
            df_display[["ID", "Название", "Автор", "Цена", "Категория", "Источник"]],
            use_container_width=True,
            height=500
        )

        csv = df_display.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 Скачать CSV",
            csv,
            "rusbuk_books.csv",
            "text/csv",
            use_container_width=True
        )

with tab2:
    st.subheader("Поиск по базе данных")

    col1, col2, col3 = st.columns(3)
    with col1:
        query = st.text_input("Название / ключевое слово")
    with col2:
        author = st.text_input("Автор")
    with col3:
        category = st.text_input("Категория")

    if st.button("Найти", type="primary"):
        results = search_books(query=query, author=author, category=category)

        if not results:
            st.warning("Ничего не найдено")
        else:
            st.success(f"Найдено: {len(results)}")
            df = pd.DataFrame(results)
            df = df.rename(columns={
                "id": "ID",
                "title": "Название",
                "author": "Автор",
                "price": "Цена",
                "category": "Категория",
                "source": "Источник"
            })
            st.dataframe(
                df[["ID", "Название", "Автор", "Цена", "Категория"]],
                use_container_width=True
            )

# ====================== ПОДВАЛ ======================
st.divider()
st.markdown("""
**Модули проекта по ТЗ:**
1. Парсер (`modules/parser.py`) — извлечение книг с Rusbuk.ru  
2. Интерфейс парсера — боковая панель  
3. Интеграция в ИС  
4. Скрипт вывода (`modules/database.py`)  
5. Интеграция вывода  
6. Интерфейс вывода — вкладки «Все книги» и «Поиск»  
7. Тестирование — провести вручную по чек-листу в ТЗ
""")
