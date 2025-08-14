# 📚 Study Tracker Dashboard

A personal study tracker web app built using **Streamlit**, **Pandas**, and **Plotly**.  
It helps you log study sessions, track hours, monitor mood trends, and get ML-based recommended study hours.  
The dashboard also includes interactive charts and fun animations to keep you motivated.

---

## ✨ Features

- **Log Study Sessions**  
  Enter Date, Topic, Mood, Target Hours, and Actual Hours (via timer or manual input).  
  All sessions are saved to a CSV file for persistent tracking.

- **ML Recommendations**  
  Predict realistic study hours for any topic based on past habits.  
  Suggests a “safe target” slightly above predicted hours.

- **Interactive Visualizations**  
  - Total study hours per topic (clustered)  
  - Mood distribution over time  
  - Target vs Actual hours per day  
  - Filter data for Today, Week, Month, or All time

- **Fun Animations**  
  Lottie animations for study motivation, toast notifications, and confetti celebrations.

---

## How It Works

1. Enter study details in the sidebar (date, topic, mood, target hours).  
2. Start the timer when you begin studying and stop it when finished.  
3. Save your session to update logs.  
4. Explore charts and ML recommendations in the main panel.

---

## ML Features Used

- **Regression**: LinearRegression & RandomForestRegressor predict study hours; DummyRegressor is fallback.  
- **Feature Engineering**: Converts moods, topic averages, and day-of-week info into numeric features.  
- **Clustering**: KMeans groups topics into high, medium, and low clusters for chart clarity.  
- **Scaling**: StandardScaler normalizes features before clustering.

---

## Installation

1. Clone the repo:  
  https://github.com/Priyankawadhwanii/study-tracker-dashboard

   cd study-tracker-dashboard
   
2.(Optional) Create a virtual environment:

Linux/Mac:

python -m venv venv

source venv/bin/activate

Windows:

python -m venv venv

venv\Scripts\activate

3.Install dependencies:

pip install -r requirements.txt

4.How to Run

streamlit run app.py


Enter your study details in the sidebar.

Use the timer to track study hours.

Save your session to update logs.

Explore charts and recommendations in the main panel.

##Dependencies
streamlit

pandas

numpy

plotly

scikit-learn

streamlit-lottie

pytz

Exact versions are in requirements.txt.

##Folder Structure
desktop
|
study_tracker
|
streamlit_app
├──.streamlit
├── app.py
├── study_data.csv
├──
├── animations/
│   ├── study.json
│   ├── toast.json
│   └── confetti.json
├── README.md
└── requirements.txt
##Future Improvements
Add subject categories to group topics better.

Track weekly or monthly study goals.

Add reminders or notifications.

Allow exporting charts as images or PDFs.

