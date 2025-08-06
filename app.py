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

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "Hours" not in st.session_state:
    st.session_state.Hours = 0.0

if "show_animation" not in st.session_state:
    st.session_state.show_animation = False


# Set page config
st.set_page_config(page_title="📚 Study Tracker Dashboard", layout="wide")

# Load animations
@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

study_animation = load_lottiefile("animations/study.json")
lottie_toast = load_lottiefile("animations/toast.json")
lottie_confetti = load_lottiefile("animations/confetti.json")

# Define database file
data_file = "study_data.csv"

# Sidebar UI
st.sidebar.title("📝 Enter Study Details")
study_date = st.sidebar.date_input("Date", value=date.today())
topic = st.sidebar.text_input("📚 Topic")
use_timer = st.sidebar.checkbox("⏱ Use Timer", value=True)
Hours = 0

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

    if use_timer and st.sidebar.button("⏹ Stop Timer") and st.session_state.start_time:
        end_time = time.time()
        elapsed_minutes = round((end_time - st.session_state.start_time) / 60, 2)
        st.session_state.Hours = round(elapsed_minutes / 60, 2)  # Converted to hours
        st.session_state.Minutes = elapsed_minutes               # Store original minutes too

        st.session_state.start_time = None
        st.success(f"✅ Study session recorded: {elapsed_minutes} minutes")

    
else:
    Hours= st.sidebar.number_input("🕒 Hours studied (manual entry)", min_value=0.0, step=0.25)

# Mood selection
mood = st.sidebar.selectbox("Mood", ["😊 Happy", "😐 Neutral", "😫 Tired", "😭 Sleepy", "😤 Frustrated", "🤩 Excited"])
target_hours = st.sidebar.number_input("Target Hours", min_value=0.0, step=0.25)

#Save button
if st.sidebar.button("✅ Save"):
    if use_timer and st.session_state.start_time is not None:
        st.warning("⛔ Please stop the timer before saving.")
    elif topic.strip() == "" or st.session_state.Hours == 0:
        st.warning("⛔ Topic field and study time cannot be empty.")
    else:
        new_data = pd.DataFrame({
            "Date": [study_date.strftime("%Y-%m-%d")],
            "Topic": [topic],
            "Hours": [st.session_state.Hours],
            "Mood": [mood],
            "Target Hours": [target_hours]
        })
    

        try:
            old_data = pd.read_csv("study_data.csv")
            df = pd.concat([old_data, new_data], ignore_index=True)
        except FileNotFoundError:
            df = new_data

        # 🔒 Backup current data before saving
        df.to_csv("study_data_backup.csv", index=False)

        # 💾 Then save the new data
        df.to_csv("study_data.csv", index=False)

        st.session_state.Hours = 0  # Reset after saving
        st.session_state.show_animation = True
        st.rerun()


# Main Dashboard
st.title("📊 Study Tracker Dashboard")

if st.session_state.get("show_animation", False):
    st_lottie(lottie_toast, height=150, key="save-toast")
    st_lottie(lottie_confetti, height=200, key="confetti")
    st.success("🎉 Well done! Your data is submitted.")
    st.session_state.show_animation = False

st_lottie(study_animation, height=200)

# Load data
if os.path.exists(data_file):
    data = pd.read_csv(data_file)
    data["Date"] = pd.to_datetime(data["Date"], dayfirst=True , errors="coerce")  # ✅ Ensures all dates are parsed
    data["Date"] = data["Date"].dt.date  #  Clean date (removes time)

    # Clean data
    data["Hours"] = pd.to_numeric(data["Hours"], errors="coerce").fillna(0)
    data["Target Hours"] = pd.to_numeric(data["Target Hours"], errors="coerce").fillna(0)

    data = data.dropna(subset=["Date", "Topic", "Hours"])  # Drop rows with missing key fields
    data = data[data["Hours"] > 0]  # Remove rows with zero hours
    data = data[data["Topic"].astype(str).str.strip() != ""]  # Remove empty topic rows
    


    st.dataframe(data)

    total_hours = data['Hours'].sum()
    st.metric("📈 Total Hours Studied", f"{total_hours:.2f} hrs")

    # Filter options
    st.markdown("### 🔍 Filter by Date")
    filter_option = st.radio("Choose a filter:", ["All", "Month", "Week", "Today"], horizontal=True)
    today = pd.Timestamp.now().normalize()

    if filter_option == "Month":
       cutoff = today - pd.DateOffset(days=30)
       filtered_data = data[data['Date'] >= cutoff]

    elif filter_option == "Week":
        filtered_data = data[pd.to_datetime(data['Date']) >= today - pd.DateOffset(days=7)]
    elif filter_option == "Today":
        filtered_data = data[pd.to_datetime(data['Date']) == today]
    else:
        filtered_data = data
    st.write("🧪 Filtered Dates:", filtered_data['Date'].unique())


    # Graph 1: Subject vs Hours
    st.markdown("### 📘 Hours Spent on Topics")
    topic_hours = filtered_data.groupby('Topic')['Hours'].sum().reset_index()
    fig_topic = px.bar(
        topic_hours,
        x='Topic',
        y='Hours',
        color='Topic',
        title=f"Total Study Hours by Topic ({filter_option})",
        color_discrete_sequence=['#FF4500', '#00008B'],
        text_auto=True
    )
    fig_topic.update_layout(
        xaxis_title='Topics',
        yaxis_title='Hours',
        title_x=0.5,
        height=450,
        font=dict(size=16),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',

        dragmode='zoom',
        showlegend=False
        
    )
    fig_topic.update_traces(marker_line_width=1.5)
    fig_topic.update_xaxes(tickangle=-45)
    fig_topic.update_layout(dragmode='zoom')
    st.plotly_chart(fig_topic, use_container_width=True)

    # Graph 2: Mood Trend (unchanged)
    st.markdown("### 😄 Mood Trend")
    mood_options = ["😊 Happy", "😐 Neutral", "😫 Tired", "😭 Sleepy", "😤 Frustrated", "🤩 Excited"]
    mood_counts = filtered_data['Mood'].value_counts().reindex(mood_options, fill_value=0)

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
# 🌟 Graph 3: Target Hours vs Actual Hours (Averaged by Date)
st.markdown("### 🌟 Target Hours vs Actual Hours (Daily Average)")

# Group by date and calculate mean
daily_avg = filtered_data.groupby("Date")[["Hours", "Target Hours"]].mean().reset_index()

# Melt for Plotly
melted = pd.melt(daily_avg, id_vars="Date", value_vars=["Hours", "Target Hours"],
                 var_name="Type", value_name="Hours Value")

# Plot using Plotly
fig = px.bar(melted, x="Date", y="Hours Value", color="Type",
             barmode="group", labels={"Hours Value": "Hours", "Date": "Date"},
             title="Average Target vs Actual Study Hours Per Day")
st.plotly_chart(fig, use_container_width=True)



#footer
st.markdown("---")
st.markdown("<div style='text-align: center;'>Made with by Priyanka Wadhwani</div>", unsafe_allow_html=True)
