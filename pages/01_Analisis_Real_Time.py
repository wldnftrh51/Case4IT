import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import gzip
import json
import time
import numpy as np
from io import BytesIO
from sklearn.ensemble import IsolationForest

st.set_page_config(page_title="📊 Analisis Real-Time", layout="wide")

st.title("📡 Dashboard Analisis Real-Time: Job Anomali")

# Fungsi untuk mengambil data dari Google Cloud Storage
@st.cache_data
def load_data():
    url = "https://storage.googleapis.com/clusterdata_2019_a/collection_events-000000000000.json.gz"
    response = requests.get(url)
    with gzip.GzipFile(fileobj=BytesIO(response.content), mode='rb') as f:
        data = [json.loads(line) for line in f]
    return pd.DataFrame(data)

# Load dataset
df_streaming = load_data()
df_streaming = df_streaming[['time', 'priority', 'scheduling_class', 'vertical_scaling', 'scheduler']].fillna(0).astype(int)
df_streaming = df_streaming.sample(frac=0.01, random_state=42).sort_values(by="time").reset_index(drop=True)

# Parameter deteksi anomali
THRESHOLD_HIGH_PRIORITY = 50
THRESHOLD_SCALING_SPIKE = 2.0
MOVING_AVG_WINDOW = 5
batch_size = 100
timestamps, anomaly_counts, history_logs, moving_avg = [], [], [], []

# Tabs untuk tampilan
tab1, tab2, tab3 = st.tabs(["📊 Grafik", "📋 Tabel Anomali", "📜 History Warning"])
chart_placeholder = tab1.empty()
table_placeholder = tab2.empty()
history_placeholder = tab3.empty()
warning_placeholder = st.empty()

# Isolation Forest Model
isolation_forest = IsolationForest(contamination=0.05, random_state=42)

for i in range(0, len(df_streaming), batch_size):
    batch = df_streaming.iloc[i:i + batch_size]
    high_priority_jobs = batch[(batch['priority'] > 100) & (batch['scheduling_class'] < 2)]
    batch['scaling_change'] = batch['vertical_scaling'].pct_change()
    scaling_anomalies = batch[batch['scaling_change'] > THRESHOLD_SCALING_SPIKE]
    batch_scheduler_anomalies = batch[(batch['priority'] > 100) & (batch['scheduler'] == 1)]
    features = batch[['priority', 'scheduling_class', 'vertical_scaling']]
    predictions = isolation_forest.fit_predict(features)
    isolation_anomalies = batch[predictions == -1]

    moving_avg.append(len(high_priority_jobs))
    if len(moving_avg) > MOVING_AVG_WINDOW:
        moving_avg.pop(0)
    avg_anomalies = np.mean(moving_avg)

    timestamps.append(batch['time'].iloc[-1])
    anomaly_counts.append(len(high_priority_jobs))

    # Update grafik utama
    fig = px.line(x=timestamps, y=anomaly_counts, markers=True, title="Jumlah Job Anomali dari Waktu ke Waktu")
    fig.update_xaxes(title="Waktu")
    fig.update_yaxes(title="Jumlah Job Anomali")
    chart_placeholder.plotly_chart(fig, use_container_width=True)

    # Tampilkan peringatan jika ada anomali
    new_warnings = []
    time_stamp = batch['time'].iloc[-1]
    
    if len(high_priority_jobs) > THRESHOLD_HIGH_PRIORITY:
        new_warnings.append(f"⚠️ {len(high_priority_jobs)} job high-priority memiliki scheduling_class rendah!")
    if len(scaling_anomalies) > 0:
        new_warnings.append(f"⚠️ {len(scaling_anomalies)} job mengalami lonjakan scaling!")
    if len(batch_scheduler_anomalies) > 0:
        new_warnings.append(f"⚠️ {len(batch_scheduler_anomalies)} job high-priority menggunakan batch scheduler!")
    if len(high_priority_jobs) > avg_anomalies * 1.5:
        new_warnings.append(f"⚠️ Anomali lonjakan job berdasarkan moving average!")
    if len(isolation_anomalies) > 0:
        new_warnings.append(f"⚠️ {len(isolation_anomalies)} anomali terdeteksi oleh Isolation Forest!")

    if new_warnings:
        warning_message = f"🕒 {time_stamp}: " + "\n".join(new_warnings)
        warning_placeholder.error(warning_message)
        history_logs.extend([{ "Time": time_stamp, "Warning": warn } for warn in new_warnings])
    
    if history_logs:
        history_df = pd.DataFrame(history_logs)
        history_placeholder.dataframe(history_df, use_container_width=True)

    if len(high_priority_jobs) > 0:
        table_placeholder.dataframe(high_priority_jobs, use_container_width=True)

    time.sleep(1)
