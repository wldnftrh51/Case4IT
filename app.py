import streamlit as st

st.set_page_config(
    page_title="Monitoring Job Anomaly",
    page_icon="📡",
    layout="wide"
)

st.sidebar.title("🔍 Navigasi")
st.sidebar.page_link("pages/01_Analisis_Real_Time.py", label="📊 Dashboard Analisis Real-Time")
st.sidebar.page_link("pages/02_Pemodelan_Prediktif.py", label="🔮 Dashboard Pemodelan Prediktif")

st.title(" Selamat Datang di Sistem Monitoring!")

# Menampilkan peran tim dalam proyek
st.subheader("👥 Tim Pengembang")
st.write("""
- **Project Manager**: Muhammad Dwino AlQadri  
- **Business Intelligence Analyst**: Wildan Hasanah  
- **Data Scientist**: Hasanah Fitrah  
- **Database Administrator**: Selwin  
- **Data Engineer**: Saputra  
- **Business User & Project Sponsor**: Dwino AlQadri  
""")