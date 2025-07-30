import streamlit as st
import pandas as pd
import time
import os
from datetime import date
from streamlit_lottie import st_lottie
import json
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Set page config
st.set_page_config(page_title="📚 Study Tracker Dashboard", layout="wide")

# Load animations
@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

study_animation = load_lottiefile("animations/study.json")
toast_animation = load_lottiefile("animations/toast.json")
confetti_animation = load_lottiefile("animations/confetti.json")

# Define database file
data_file = "study_data.csv"

# Sidebar UI
st.sidebar.title("📝 Enter Study Details")
study_date = st.sidebar.date_input("Date", value=date.today())
topic = st.sidebar.text_input("📚 Topic")
use_timer = st.sidebar.checkbox("⏱ Use Timer", value=True)
duration = 0

# Timer logic
if use_timer:
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'timer_display' not in st.session_state:
        st.session_state.timer_display = "00:00:00"

    if st.sidebar.button("▶ Start Timer"):
        st.session_state.start_time = time.time()

    if st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)
        mins, secs = divmod(elapsed, 60)
        hrs, mins = divmod(mins, 60)
        st.session_state.timer_display = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        st.sidebar.markdown(f"### 🕒 Elapsed Time: {st.session_state.timer_display}")

    if st.sidebar.button("⏹ Stop Timer") and st.session_state.start_time:
        Hours = round((time.time() - st.session_state.start_time) / 60, 2)
        st.session_state.start_time = None
        st.success(f"Session Hours: {Hours} minutes")
else:
    Hours= st.sidebar.number_input("🕒 Hours (minutes)", min_value=0, step=5)

# Mood selection

mood = st.sidebar.selectbox("Mood", ["😊 Happy", "😐 Neutral", "😫 Tired", "😴 Sleepy", "😤 Frustrated", "🤩 Excited"])
target_hours = st.sidebar.number_input("Target Hours", min_value=0.0, step=0.5)

if st.sidebar.button("Save"):
    if topic and ("hours" in st.session_state):
        new_entry = pd.DataFrame({
            "Date": [study_date],
            "Topic": [topic],
            "Hours": [st.session_state.hours],
            "Mood": [mood],
            "Target": [target_hours]
        })

        if os.path.exists(data_file):
            new_entry.to_csv(data_file, mode='a', header=False, index=False)
        else:
            new_entry.to_csv(data_file, index=False)

        st.success("Well done! Your data is submitted.")
        st_lottie(confetti_animation, height=200)
        st_lottie(toast_animation, height=150)
    else:
        st.error("Please fill in all the fields before saving.")

# Main Dashboard
st.title("📊 Study Tracker Dashboard")
st_lottie(study_animation, height=200)

# Load data
if os.path.exists(data_file):
    data = pd.read_csv(data_file)
    st.dataframe(data)

    total_hours = data['Hours'].sum()
    st.metric("📈 Total Hours Studied", f"{total_hours:.2f} hrs")

    # Topic Pie Chart
    st.markdown("### 📚 Topics Studied")
    fig1, ax1 = plt.subplots()
    data['Topic'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax1)
    ax1.set_ylabel('')
    st.pyplot(fig1)

    # Mood Graph
    mood_options = ["😊 Happy", "😐 Neutral", "😫 Tired", "😴 Sleepy", "😤 Frustrated", "🤩 Excited"]
    mood_counts = data['Mood'].value_counts().reindex(mood_options, fill_value=0)

    st.markdown("### 😄 Mood Trend")
    fig_mood = px.bar(
        x=mood_counts.index,
        y=mood_counts.values,
        color=mood_counts.index,
        color_discrete_sequence=["#90ee90", "#d3d3d3", "#f4a460", "#add8e6", "#ff6961", "#dda0dd"],
        labels={'x': 'Mood', 'y': 'Count'},
        title="Your Mood Distribution Over Time",
    )

    fig_mood.update_layout(
        xaxis_title='Mood',
        yaxis_title='Number of Logs',
        title_x=0.5,
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=16),
        margin=dict(t=50, l=30, r=30, b=30),
        showlegend=False
    )

    st.plotly_chart(fig_mood, use_container_width=True)
else:
    st.warning("No study data found. Start logging your study sessions!")

#footer
st.markdown("---")
st.markdown("<div style='text-align: center;'>Made with ❤️ by Priyanka</div>", unsafe_allow_html=True)
   
