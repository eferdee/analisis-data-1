import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import os

sns.set(style="white")

#Fungsi Pertanyaan 1: Penggunaan Sepeda terhadap Kondisi Cuaca
def weather_impact(df):
    plt.figure(figsize=(10, 5))
    sns.barplot(data=df, x='weathersit_x', y='cnt_x')
    plt.title('Distribusi Penggunaan Sepeda Berdasarkan Kondisi Cuaca')
    plt.xlabel('Kondisi Cuaca')
    plt.ylabel('Penggunaan Sepeda')
    plt.xticks(ticks=[0,1,2], labels=['Cerah', 'Mendung', 'Hujan'])
    st.pyplot(plt)

    
#Fungsi Pertanyaan 2: Penggunaan Sepeda per Hari dalam Satu Pekan
def usage_by_day_of_week(df):
    daily_usage = df.groupby('dteday')['cnt_x'].sum().reset_index()
    daily_usage['day_of_week'] = daily_usage['dteday'].dt.day_name()
    weekly_usage = daily_usage.groupby('day_of_week')['cnt_x'].mean().reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    plt.figure(figsize=(12, 6))
    sns.barplot(x=weekly_usage.index, y=(weekly_usage.values/24))
    plt.title('Rata-Rata Penggunaan Sepeda per Hari dalam Satu Pekan')
    plt.xlabel('Hari dalam Satu Pekan')
    plt.ylabel('Rata-Rata Penggunaan Sepeda')
    st.pyplot(plt)

# Memuat data
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Path relatif ke main_data.csv
    DATA_PATH = os.path.join(base_dir, "main_data.csv")
    return pd.read_csv(DATA_PATH)

# Memuat data
all_df = load_data()
all_df["dteday"] = pd.to_datetime(all_df["dteday"])

# Filter tanggal
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

# Sidebar untuk pemilihan tanggal
with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu', 
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan rentang tanggal yang dipilih
filtered_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                     (all_df["dteday"] <= str(end_date))]

st.header('Dashboard Bike Sharing')
st.subheader('Data Penggunaan Sepeda Terhadap Kondisi Cuaca')
weather_impact(filtered_df)
# Menambahkan penjelasan
st.write("""
Berdasarkan dari keseluruhan data yang ada pada dataset, distribusi penggunaan sepeda lebih banyak apabila cuaca nya lebih bagus. Penggunaan sepeda akan lebih banyak apabila cuaca hari bagus (cerah), semakin sedikit ketika mendung, dan semakin sedikit lagi ketika hujan.
""")

st.subheader('Penggunaan Sepeda Berdasarkan Hari dalam Satu Pekan')
usage_by_day_of_week(filtered_df)
# Menambahkan penjelasan
st.write("""
Berdasarkan dari keseluruhan data yang ada pada dataset, terdapat lonjakan penggunaan sepeda pada hari kerja (Senin s.d. Jumat) jauh lebih besar dibandingkan dengan hari libur (Sabtu dan Ahad).
""")

st.caption('Analisis Data Penggunaan Sepeda -- M. Farid Saputra')
