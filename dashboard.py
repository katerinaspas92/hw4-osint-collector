import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent / "osint_data.db"

st.set_page_config(
    page_title="OSINT Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 OSINT Dashboard")
st.caption("Статистика публичных публикаций Mastodon")


@st.cache_data(ttl=60)
def load_data():
    if not DB_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as db:
        data = pd.read_sql_query(
            "SELECT id, author, url, date, text FROM posts",
            db,
        )

    return data


df = load_data()

if df.empty:
    st.warning("База данных отсутствует или в ней нет публикаций.")
    st.stop()

df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")

# Основные показатели
total_posts = len(df)
unique_authors = df["author"].nunique()

valid_dates = df["date"].dropna()

earliest = valid_dates.min() if not valid_dates.empty else None
latest = valid_dates.max() if not valid_dates.empty else None

col1, col2, col3, col4 = st.columns(4)

col1.metric("Публикаций", total_posts)
col2.metric("Уникальных авторов", unique_authors)
col3.metric(
    "Первая публикация",
    earliest.strftime("%d.%m.%Y") if earliest is not None else "Нет данных",
)
col4.metric(
    "Последняя публикация",
    latest.strftime("%d.%m.%Y") if latest is not None else "Нет данных",
)

st.divider()

# График публикаций по дням
st.subheader("📈 Публикации по дням")

daily = (
    df.dropna(subset=["date"])
    .assign(day=lambda data: data["date"].dt.date)
    .groupby("day")
    .size()
    .rename("Количество публикаций")
)

if not daily.empty:
    st.bar_chart(daily)
else:
    st.info("Нет корректных дат для построения графика.")

# Самые активные авторы
st.subheader("🏆 Топ-10 авторов")

top_authors = df["author"].value_counts().head(10)

st.bar_chart(top_authors)

st.divider()

# Поиск по публикациям
st.subheader("🔍 Поиск публикаций")

search = st.text_input(
    "Введите слово или часть текста",
    placeholder="Например: python",
)

filtered = df.copy()

if search:
    filtered = filtered[
        filtered["text"]
        .fillna("")
        .str.contains(search, case=False, regex=False)
    ]

st.write(f"Найдено публикаций: **{len(filtered)}**")

# Таблица
st.subheader("📋 Собранные публикации")

filtered = filtered.sort_values("date", ascending=False)

st.dataframe(
    filtered[["author", "date", "url", "text"]],
    width="stretch",
    hide_index=True,
    column_config={
        "url": st.column_config.LinkColumn("Ссылка"),
    },
)

# Выгрузка результатов поиска
st.download_button(
    label="⬇️ Скачать результаты поиска (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="filtered_posts.csv",
    mime="text/csv",
)
