from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import time

# --- Streamlit Page Settings ---
st.set_page_config(page_title="📚 Priyanka's Personal Study Tracker", page_icon="✨")

# --- Connect to SQLite Database ---
conn = sqlite3.connect("study_tracker.db", check_same_thread=False)
cursor = conn.cursor()

# --- Create Table if not exists ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    start_time TEXT,
    end_time TEXT,
    duration REAL,
    topic TEXT,
    mood TEXT
)
''')
conn.commit()

# --- Function to Calculate Study Streak ---
def calculate_study_streak(dates):
    if dates.empty:
        return 0
    dates = sorted(set(pd.to_datetime(dates).dt.normalize()), reverse=True)
    today = datetime.now().date()
    streak = 0
    for i, date in enumerate(dates):
        if date.date() == today - timedelta(days=i):
            streak += 1
        else:
            break
    return streak

# --- Title ---
st.title("📚 Personal Study Tracker Dashboard")
st.markdown("Keep tracking your progress, little steps matter! 🚶‍♀️✨")

# --- Timer with persistent storage ---
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

st.subheader("🎯 Real-Time Study Timer")
topic = st.text_input("What are you studying?")
mood = st.radio("How are you feeling?", ["😄 Happy", "😫 Tired", "😌 Calm", "😤 Frustrated"])

col1, col2, col3 = st.columns(3)
if col1.button("▶️ Start"):
    if not st.session_state.timer_running:
        st.session_state.start_time = datetime.now()
        st.session_state.timer_running = True
        st.success("Timer started!")

if col2.button("⏸️ Stop"):
    if st.session_state.timer_running:
        end_time = datetime.now()
        duration = (end_time - st.session_state.start_time).total_seconds() / 3600
        cursor.execute('''
            INSERT INTO study_sessions (date, start_time, end_time, duration, topic, mood)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d'),
            st.session_state.start_time.strftime('%H:%M:%S'),
            end_time.strftime('%H:%M:%S'),
            round(duration, 2),
            topic,
            mood
        ))
        conn.commit()
        st.success(f"Saved! Duration: {round(duration, 2)} hours")
        st.session_state.timer_running = False
        st.session_state.start_time = None

if col3.button("🔄 Reset"):
    st.session_state.timer_running = False
    st.session_state.start_time = None

# --- Display current timer ---
if st.session_state.timer_running:
    elapsed = (datetime.now() - st.session_state.start_time).total_seconds() / 3600
else:
    elapsed = 0

st.metric("⏳ Timer", f"{elapsed:.2f} hrs")

# --- Load Data from Database ---
df = pd.read_sql_query("SELECT * FROM study_sessions", conn)
df['date'] = pd.to_datetime(df['date'])

# --- Sidebar Filters ---
st.sidebar.header("Filters 🎛️")
selected_mood = st.sidebar.multiselect("Select Mood:", df['mood'].unique())
selected_topics = st.sidebar.multiselect("Select Topics:", df['topic'].unique())

filtered_df = df.copy()
if selected_mood:
    filtered_df = filtered_df[filtered_df['mood'].isin(selected_mood)]
if selected_topics:
    filtered_df = filtered_df[filtered_df['topic'].isin(selected_topics)]

# --- Study Summary ---
st.markdown("## 🏆 Study Summary")
total_hours = filtered_df['duration'].sum()
days_count = filtered_df['date'].nunique()
avg_hours = total_hours / days_count if days_count else 0
streak = calculate_study_streak(filtered_df['date'])

col1, col2, col3, col4 = st.columns(4)
col1.metric("📆 Total Hours", f"{total_hours:.1f} hrs")
col2.metric("⏳ Avg/Day", f"{avg_hours:.1f} hrs")
col3.metric("🔥 Streak", f"{streak} days")
col4.metric("📚 Sessions", f"{len(filtered_df)}")

# --- Show Table ---
st.subheader("📝 Study Sessions")
st.dataframe(filtered_df)

# --- Charts ---
st.subheader("📈 Study Hours Over Time")
fig = px.line(filtered_df, x='date', y='duration', markers=True, title="Study Hours Trend")
st.plotly_chart(fig)

st.subheader("😊 Mood Distribution")
mood_df = filtered_df['mood'].value_counts().reset_index()
mood_df.columns = ['Mood', 'Count']
fig2 = px.bar(mood_df, x='Mood', y='Count', color='Mood', title="Mood Patterns")
st.plotly_chart(fig2)

# --- Footer ---
st.markdown("---")
st.caption("Built by Priyanka ✨ Stay consistent, stay awesome!")
