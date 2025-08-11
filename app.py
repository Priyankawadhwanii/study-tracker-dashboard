import streamlit as st
import pandas as pd
import time
import os
from datetime import date, datetime
from streamlit_lottie import st_lottie
import json
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

# Initialize session state
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "Hours" not in st.session_state:
    st.session_state.Hours = 0.0
if "show_toast" not in st.session_state:
    st.session_state.show_toast = False

# Load or create data
csv_file = "study_data.csv"
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
else:
    df = pd.DataFrame(columns=["Date", "Topic", "Hours", "Mood", "Target Hours"])
#sidebar
st.sidebar.title("📋 Enter Study Details")

# Date input
study_date = st.sidebar.date_input("📅 Date", date.today())
# Topic input
topic = st.sidebar.text_input("📚 Topic", key="topic_name")

mood = None
if topic:
    mood_options = [
        "😊 Happy", "😐 Neutral", "😫 Tired", "😴 Sleepy", "😤 Frustrated", "🤩 Excited"
    ]

    # Mood selectbox that returns value
    mood = st.sidebar.selectbox("😄 Mood", mood_options, key="mood_select")

    # Auto-focus on mood dropdown after topic is entered
    st.sidebar.markdown(
        """
        <script>
        setTimeout(function(){
            var moodBox = window.parent.document.querySelector('select[data-baseweb="select"]');
            if(moodBox){ moodBox.focus(); }
        }, 100);
        </script>
        """,
        unsafe_allow_html=True
    )



# Checkbox for timer usage
use_timer = st.sidebar.checkbox("⏱️ Use Timer", value=True)

# Target hours input
target_hours = st.sidebar.number_input("🎯 Target Hours", min_value=0.0, step=0.25)


# Timer logic
from datetime import datetime
import pytz  # <-- Add this import at the top

# Define Indian timezone
indian_tz = pytz.timezone("Asia/Kolkata")

# Timer controls
recorded_time = 0.0
if use_timer:
    if st.sidebar.button("▶️ Start"):
        st.session_state.start_time = time.time()
        st.session_state.start_clock_time = datetime.now(indian_tz).strftime('%H:%M:%S')  # Save start clock time
        st.success(f"Started recording study time at {st.session_state.start_clock_time} IST")

    if st.session_state.start_time:
        st.sidebar.write(f"⏳ Time started at: {st.session_state.start_clock_time} IST")

    if st.sidebar.button("⏹️ Stop"):
        if st.session_state.start_time:
            end_time = time.time()
            recorded_time = round((end_time - st.session_state.start_time) / 3600, 2)
            st.session_state.Hours = recorded_time
            stop_clock_time = datetime.now(indian_tz).strftime('%H:%M:%S')
            st.success(f"Study time recorded: {recorded_time} hours (Stopped at {stop_clock_time} IST)")
            st.session_state.start_time = None
        else:
            st.warning("Start the timer first!")


# Save Entry
if st.sidebar.button("💾 Save"):
    new_entry = pd.DataFrame({
        "Date": [study_date],
        "Topic": [topic],
        "Hours": [st.session_state.Hours],
        "Mood": [mood],
        "Target Hours": [target_hours]
    })
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(csv_file, index=False)
    st.session_state.show_toast = True

# Main Dashboard
st.title("📚 Study Tracker Dashboard")

if st.session_state.show_toast:
    st.balloons()
    st_lottie(confetti_animation, height=150, key="confetti")
    st_lottie(toast_animation, height=100, key="toast")
    st.success("✅ Well done! Your data is submitted.")
    st.session_state.show_toast = False

st_lottie(study_animation, height=300, key="study")

# Filters
st.subheader("🔍 Filter Study Data")
filter_option = st.radio("Choose Filter", ("All", "Month", "Week", "Today"), horizontal=True)

today = date.today()
filtered_data = df.copy()

if filter_option == "Today":
    filtered_data = df[df["Date"] == today]
elif filter_option == "Week":
    filtered_data = df[df["Date"] >= today - pd.Timedelta(days=7)]
elif filter_option == "Month":
    filtered_data = df[(pd.to_datetime(df["Date"]).dt.month == today.month) & 
                       (pd.to_datetime(df["Date"]).dt.year == today.year)]

# Study History Table
st.markdown("### 📈 Study History")
st.dataframe(filtered_data.sort_values("Date", ascending=False))

# Summary
total_hours = filtered_data["Hours"].sum()
st.markdown(f"### ⏳ Total Hours Studied: **{total_hours:.2f} Hours**")

# Graph 1: Topic vs Hours
st.markdown("### 📘 Hours Spent on Topics")
if not filtered_data.empty:
    topic_hours = filtered_data.groupby('Topic')['Hours'].sum().reset_index()
    fig_topic = px.bar(
        topic_hours,
        x='Topic',
        y='Hours',
        color='Topic',
        title=f"Total Study Hours by Topic ({filter_option})",
        text_auto=True
    )
    fig_topic.update_layout(
    xaxis_title='Topics',
    yaxis_title='Hours',
    title_x=0.5,
    height=450,
    showlegend=False  
    )
    fig_topic.update_layout(xaxis_title='Topics', yaxis_title='Hours', title_x=0.5, height=450)
    fig_topic.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_topic, use_container_width=True)
    

# Graph 2: Mood Trend
st.markdown("### 😄 Mood Trend")
mood_options = ["😊 Happy", "😐 Neutral", "😫 Tired", "😴 Sleepy", "😤 Frustrated", "🤩 Excited"]
mood_counts = filtered_data['Mood'].value_counts().reindex(mood_options, fill_value=0)

fig_mood = px.bar(
    x=mood_counts.index,
    y=mood_counts.values,
    color=mood_counts.index,
    color_discrete_sequence=["#90ee90", "#d3d3d3", "#f4a460", "#add8e6", "#ff6961", "#dda0dd"],
    labels={'x': 'Mood', 'y': 'Count'},
    title="Your Mood Distribution Over Time",
)
fig_mood.update_layout(xaxis_title='Mood', yaxis_title='Number of Logs', title_x=0.5, height=450, showlegend=False)
st.plotly_chart(fig_mood, use_container_width=True)

# Graph 3: Target vs Actual Hours (Daily Avg)
st.markdown("### 🌟 Target Hours vs Actual Hours (Daily Average)")
daily_avg = filtered_data.groupby("Date")[["Hours", "Target Hours"]].mean().reset_index()
melted = pd.melt(daily_avg, id_vars="Date", value_vars=["Hours", "Target Hours"],
                 var_name="Type", value_name="Hours Value")
fig_comparison = px.bar(
    melted,
    x="Date",
    y="Hours Value",
    color="Type",
    barmode="group",
    title="Average Target vs Actual Study Hours Per Day"
)
fig_comparison.update_layout(xaxis_title="Date", yaxis_title="Hours", title_x=0.5, height=450)
st.plotly_chart(fig_comparison, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center;'>Made by Priyanka Wadhwani</div>", unsafe_allow_html=True)  
