import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

st.set_page_config(page_title="🔮 Pemodelan Prediktif", layout="wide")

st.title("🔮 Dashboard Pemodelan Prediktif")

# Simulasi data anomali (real-nya harus diambil dari dashboard real-time)
@st.cache_data
def load_anomaly_data():
    np.random.seed(42)
    timestamps = list(range(1, 101))
    anomaly_counts = np.random.randint(0, 50, size=100)
    return pd.DataFrame({"time": timestamps, "anomalies": anomaly_counts})

df_anomaly = load_anomaly_data()

# Input user untuk prediksi
prediction_horizon = st.sidebar.slider("Pilih horizon prediksi:", 10, 50, 20)
predict_button = st.sidebar.button("🔍 Prediksi")

# Plot data historis
st.subheader("📈 Data Historis Anomali")
fig_hist = px.line(df_anomaly, x="time", y="anomalies", markers=True, title="Jumlah Anomali Historis")
st.plotly_chart(fig_hist, use_container_width=True)

# Prediksi ARIMA
if predict_button:
    series = df_anomaly["anomalies"]
    model = ARIMA(series, order=(5, 1, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=prediction_horizon)

    pred_timestamps = list(range(101, 101 + prediction_horizon))
    fig_pred = px.line(x=pred_timestamps, y=forecast, markers=True, title="Prediksi Jumlah Job Anomali")
    fig_pred.update_xaxes(title="Waktu")
    fig_pred.update_yaxes(title="Prediksi Jumlah Job Anomali")

    st.subheader("🔮 Hasil Prediksi")
    st.plotly_chart(fig_pred, use_container_width=True)
