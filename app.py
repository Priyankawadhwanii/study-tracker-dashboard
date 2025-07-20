
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import random

st.markdown(
    """
    <style>
    .main {
        background-color: #f8f4fc;
        color: #4b0082;
    }
    .st-cb {
        background-color: #e7defe !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Motivational Quotes ---
quotes = [
    "Consistency beats motivation. 🚀",
    "Small progress each day adds up to big results. 💪",
    "Study like your future depends on it. Because it does. ✨",
    "Discipline is choosing between what you want now and what you want most. 🔥",
    "Stay patient and trust your journey. 🛤️"
]

# --- App Title ---
st.set_page_config(page_title="Study Tracker", page_icon="📚", layout="wide")
st.title("📚 Personal Study Tracker Dashboard")

# --- Load Data ---
data_file = "data/study_data.csv"

if os.path.exists(data_file):
    df = pd.read_csv(data_file)
    df['Date'] = pd.to_datetime(df['Date'])
else:
    st.warning("No data file found. Please ensure 'study_data.csv' exists inside the 'data' folder.")
    st.stop()

# --- Sidebar ---
st.sidebar.header("Filters 🎛️")
selected_mood = st.sidebar.multiselect("Filter by Mood:", df['Mood'].unique())
selected_topics = st.sidebar.multiselect("Filter by Topic:", df['Topic'].unique())

filtered_df = df.copy()
if selected_mood:
    filtered_df = filtered_df[filtered_df['Mood'].isin(selected_mood)]
if selected_topics:
    filtered_df = filtered_df[filtered_df['Topic'].isin(selected_topics)]

# --- Motivation Quote Section ---
st.markdown("### 💡 Today's Motivation")
st.success(random.choice(quotes))

# --- Summary Metrics Section ---
st.markdown("## 🏆 Your Study Summary")

# This week's hours
today = datetime.today()
week_ago = today - timedelta(days=7)
this_week = df[df['Date'] >= week_ago]
total_hours_week = this_week['Hours_Studied'].sum()

# Productivity badge logic
avg_hours = this_week['Hours_Studied'].mean()
if avg_hours >= 3:
    badge = "🔥 On Fire!"
elif avg_hours >= 2:
    badge = "✅ Consistent!"
else:
    badge = "💤 Could Improve!"

col1, col2, col3 = st.columns(3)
col1.metric("📆 This Week's Hours", f"{total_hours_week} hrs")
col2.metric("⏳ Avg Hours / Day", f"{avg_hours:.1f} hrs")
col3.metric("🏅 Productivity Badge", badge)

# --- Study Streak Logic ---
streak = 0
df_sorted = df.sort_values(by='Date', ascending=False)
for date in df_sorted['Date']:
    if (today - date).days == streak:
        streak += 1
    else:
        break
st.markdown(f"### 🔥 Current Study Streak: **{streak} days**")

# --- Show Data Table ---
st.markdown("---")
st.subheader("📑 Filtered Study Data")
st.dataframe(filtered_df)

# --- Study Hours Visualization ---
st.markdown("## 📊 Study Hours Over Time")
st.line_chart(filtered_df.set_index('Date')['Hours_Studied'])

# --- Mood Visualization ---
st.markdown("## 😄 Mood Distribution")
st.bar_chart(filtered_df['Mood'].value_counts())

# --- Difficulty Level ---
st.markdown("## 📈 Average Difficulty Level")
st.write(f"Average Difficulty: **{filtered_df['Difficulty (1-5)'].mean():.2f} / 5**")

# --- Footer ---
st.markdown("---")
st.caption("✨ Built with ❤️ using Streamlit")




