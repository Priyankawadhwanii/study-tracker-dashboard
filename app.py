import streamlit as st
import pandas as pd
import time
import os
from datetime import date, datetime
from streamlit_lottie import st_lottie
import json
import plotly.express as px
import pytz  # IST timezone

# ML imports
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyRegressor
import numpy as np

# ---------------- Page setup ----------------
st.set_page_config(page_title="📚 Study Tracker Dashboard", layout="wide")

@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

study_animation = load_lottiefile("animations/study.json")
toast_animation = load_lottiefile("animations/toast.json")
confetti_animation = load_lottiefile("animations/confetti.json")

# ---------------- Session state ----------------
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "Hours" not in st.session_state:
    st.session_state.Hours = 0.0
if "show_toast" not in st.session_state:
    st.session_state.show_toast = False

# ---------------- Load data ----------------
csv_file = "study_data.csv"
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file, parse_dates=["Date"], dayfirst=True)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
else:
    df = pd.DataFrame(columns=["Date", "Topic", "Hours", "Mood", "Target Hours"])    


# ---------------- ML helper functions ----------------
def safe_mood_score(mood_str):
    mapping = {
        "😊 Happy": 2, "😐 Neutral": 1, "😫 Tired": 0,
        "😴 Sleepy": 0, "😤 Frustrated": 0, "🤩 Excited": 2
    }
    return mapping.get(mood_str, 1)

def prepare_ml_table(df):
    df2 = df.copy()
    df2["Hours"] = pd.to_numeric(df2["Hours"], errors="coerce").fillna(0.0)
    df2["Target Hours"] = pd.to_numeric(df2["Target Hours"], errors="coerce").fillna(0.0)
    df2["Date"] = pd.to_datetime(df2["Date"], errors="coerce")

    topic_avg = df2.groupby("Topic")["Hours"].mean()
    df2["topic_avg"] = df2["Topic"].map(topic_avg).fillna(df2["Hours"].mean())

    df2["day_of_week"] = df2["Date"].dt.dayofweek.fillna(0).astype(int)
    df2["mood_score"] = df2["Mood"].apply(safe_mood_score)

    X = df2[["topic_avg", "Target Hours", "day_of_week", "mood_score"]]
    y = df2["Hours"]
    return X, y, topic_avg

def train_regressor(X, y):
    # If very little data, LinearRegression is fine; otherwise RandomForest
    if len(X) < 6:
        model = LinearRegression().fit(X, y)
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, y)
    return model

def recommend_target_hours(model, topic_avg_series, topic_name, chosen_target, mood_str, date_obj):
    topic_avg_val = topic_avg_series.get(topic_name, topic_avg_series.mean() if len(topic_avg_series) > 0 else 0.5)
    day_of_week = pd.to_datetime(date_obj).dayofweek if date_obj is not None else 0
    mood_score = safe_mood_score(mood_str)
    X_in = pd.DataFrame(
    [[topic_avg_val, float(chosen_target), int(day_of_week), int(mood_score)]],
    columns=["topic_avg", "Target Hours", "day_of_week", "mood_score"]
)

    pred_hours = float(model.predict(X_in)[0])
)
  # Always base recommended on model prediction (not just copying target)
    recommended = round(pred_hours * 1.10, 2)
    return pred_hours, recommended


def compute_topic_clusters(df, n_clusters=3):
    df_num = df.copy()
    df_num["Hours"] = pd.to_numeric(df_num["Hours"], errors="coerce").fillna(0.0)
    agg = df_num.groupby("Topic").agg(mean_hours=("Hours", "mean"), sessions=("Hours", "count")).fillna(0)
    if len(agg) == 0:
        return {}
    if len(agg) < n_clusters:
        n_clusters = max(1, len(agg))
    X = StandardScaler().fit_transform(agg[["mean_hours", "sessions"]])
    labels = KMeans(n_clusters=n_clusters, random_state=42).fit_predict(X)
    agg["cluster"] = labels
    return agg["cluster"].to_dict()



# -------------- end helpers ----------------

# -------------- Sidebar inputs --------------
st.sidebar.title("📋 Enter Study Details")
study_date = st.sidebar.date_input("📅 Date", date.today())
topic = st.sidebar.text_input("📚 Topic", key="topic_name")

mood = None
if topic:
    mood = st.sidebar.selectbox(
        "😄 Mood",
        ["😊 Happy", "😐 Neutral", "😫 Tired", "😴 Sleepy", "😤 Frustrated", "🤩 Excited"],
        key="mood_select"
    )
    # UI hint: tries to focus mood after topic (may not work reliably due to reruns)
    st.sidebar.markdown(
        """
        <script>
        setTimeout(function(){
            var el = window.parent.document.querySelector('select');
            if(el){ el.focus(); }
        }, 100);
        </script>
        """,
        unsafe_allow_html=True
    )

use_timer = st.sidebar.checkbox("⏱️ Use Timer", value=True)



# -------------- Timer (IST) --------------
indian_tz = pytz.timezone("Asia/Kolkata")
recorded_time = 0.0
if use_timer:
    if st.sidebar.button("▶️ Start"):
        st.session_state.start_time = time.time()
        st.session_state.start_clock_time = datetime.now(indian_tz).strftime('%H:%M:%S')
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
else:
   # Manual entry
    manual_hours = st.sidebar.number_input("⏱️ Enter study hours manually", min_value=0.0, step=0.25)
    st.session_state.Hours = manual_hours


target_hours = st.sidebar.number_input("🎯 Target Hours", min_value=0.0, step=0.25)    
# -------------- Save row --------------
if st.sidebar.button("💾 Save"):
    new_entry = pd.DataFrame({
        "Date": [study_date],
        "Topic": [topic],
        "Hours": [st.session_state.Hours],
        "Mood": [mood],
        "Target Hours": [target_hours],
        "Manual Hours" : [manual_hours]
        
    })
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(csv_file, index=False)
    st.session_state.show_toast = True

# -------------- Main header & confetti --------------
st.title("📚 Study Tracker Dashboard")
if st.session_state.show_toast:
    st.balloons()
    st_lottie(confetti_animation, height=150, key="confetti")
    st_lottie(toast_animation, height=100, key="toast")
    st.success("✅ Well done! Your data is submitted.")
    st.session_state.show_toast = False

st_lottie(study_animation, height=300, key="study")

# -------------- Train ML BEFORE using it --------------
if not df.empty:
    X, y, topic_avg_series = prepare_ml_table(df)
    if len(X) > 0:
        # Fit a real model; if data is degenerate, fall back to mean-predictor (but still fit)
        try:
            reg_model = train_regressor(X, y)
        except Exception:
            reg_model = DummyRegressor(strategy="mean").fit(X, y)
    else:
        reg_model = None
    topic_cluster_map = compute_topic_clusters(df, n_clusters=3)
else:
    reg_model = None
    topic_avg_series = pd.Series(dtype=float)
    topic_cluster_map = {}

#ML panel
with st.expander("🔮 ML Suggestions & Recommendations", expanded=True):
    st.write("Get a recommended target for a topic based on your past logs.")

    demo_topic = topic
    demo_mood = mood
    demo_date = study_date
    demo_target = target_hours

    st.write(f"📚 Topic: {demo_topic or '(not set)'}")
    st.write(f" Mood: {demo_mood or '(not set)'}")
    st.write(f" Date: {demo_date}")
    st.write(f"Target Hours: {demo_target}")

    if st.button("➡️ Recommend target hours"):
        if reg_model is None or (demo_topic.strip() == ""):
            st.info("Not enough data yet or topic missing. Add some logs and try again.")
        else:
            pred_hours, recommended_target = recommend_target_hours(
                reg_model, topic_avg_series, demo_topic, demo_target, demo_mood, demo_date
            )
            st.info(f"Recommended target (safe): **{recommended_target:.2f}**")

# -------------- Filters --------------
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

# -------------- Table & KPIs --------------
st.markdown("### 📈 Study History")
st.dataframe(filtered_data.sort_values("Date", ascending=False))

total_hours = pd.to_numeric(filtered_data["Hours"], errors="coerce").fillna(0.0).sum()
st.markdown(f"### ⏳ Total Hours Studied: **{total_hours:.2f} Hours**")

# -------------- Charts --------------
st.markdown("### 📘 Hours Spent on Topics (clustered)")
if not filtered_data.empty:
    topic_hours = filtered_data.groupby('Topic', as_index=False)['Hours'].sum()
    topic_hours["cluster"] = topic_hours["Topic"].map(topic_cluster_map).fillna(-1).astype(int)

    fig_topic = px.bar(
        topic_hours.sort_values("Hours", ascending=False),
        x='Topic', y='Hours', color='cluster',
        title=f"Total Study Hours by Topic ({filter_option})",
        text_auto=True
    )
    fig_topic.update_layout(xaxis_title='Topics', yaxis_title='Hours', title_x=0.5, height=450, showlegend=True)
    fig_topic.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_topic, use_container_width=True)

st.markdown("### 😄 Mood Trend")
mood_options = ["😊 Happy", "😐 Neutral", "😫 Tired", "😴 Sleepy", "😤 Frustrated", "🤩 Excited"]
mood_counts = filtered_data['Mood'].value_counts().reindex(mood_options, fill_value=0)
fig_mood = px.bar(
    x=mood_counts.index, y=mood_counts.values, color=mood_counts.index,
    color_discrete_sequence=["#90ee90", "#d3d3d3", "#f4a460", "#add8e6", "#ff6961", "#dda0dd"],
    labels={'x': 'Mood', 'y': 'Count'}, title="Your Mood Distribution Over Time"
)
fig_mood.update_layout(xaxis_title='Mood', yaxis_title='Number of Logs', title_x=0.5, height=450, showlegend=False)
st.plotly_chart(fig_mood, use_container_width=True)

st.markdown("### 🌟 Target Hours vs Actual Hours (Daily Average)")
daily_avg = filtered_data.groupby("Date")[["Hours", "Target Hours"]].mean().reset_index()
melted = pd.melt(daily_avg, id_vars="Date", value_vars=["Hours", "Target Hours"],
                 var_name="Type", value_name="Hours Value")
fig_comparison = px.bar(
    melted, x="Date", y="Hours Value", color="Type", barmode="group",
    title="Average Target vs Actual Study Hours Per Day"
)
fig_comparison.update_layout(xaxis_title="Date", yaxis_title="Hours", title_x=0.5, height=450)
st.plotly_chart(fig_comparison, use_container_width=True)

# -------------- Footer --------------
st.markdown("---")
st.markdown("<div style='text-align: center;'>Made by Priyanka Wadhwani</div>", unsafe_allow_html=True)
