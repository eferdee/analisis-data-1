import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="white")

def create_rfm_df(df):
    # Menggunakan kolom 'dteday' dan 'cnt' untuk menghitung RFM
    rfm_df = df.groupby(by=["dteday"], as_index=False).agg({
        "cnt": "sum"  # Total penggunaan sepeda
    })
    
    rfm_df.columns = ["dteday", "monetary"]
    
    rfm_df["dteday"] = pd.to_datetime(rfm_df["dteday"])
    recent_date = df["dteday"].max()
    rfm_df["recency"] = (recent_date - rfm_df["dteday"]).dt.days
    
    # Menghitung frekuensi berdasarkan jumlah entri (baris) per tanggal
    rfm_df["frequency"] = df.groupby("dteday")["cnt"].count().values  # Menambahkan kolom frekuensi

    return rfm_df

# Load cleaned data
day_df = pd.read_csv("day.csv")
hour_df = pd.read_csv("hour.csv")

# Menggabungkan data dari kedua dataset
combined_df = pd.concat([day_df, hour_df], ignore_index=True)

# Mengubah kolom dteday menjadi tipe datetime
combined_df["dteday"] = pd.to_datetime(combined_df["dteday"])

# Filter data
min_date = combined_df["dteday"].min()
max_date = combined_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://contents.mediadecathlon.com/p2228270/k$910d8cfe0711fc7768658d32122920fe/sepeda-gunung-st-530-27-5-9-kecepatan-merah-rockrider-8585187.jpg?f=1920x0&format=auto")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = combined_df[(combined_df["dteday"] >= str(start_date)) & 
                      (combined_df["dteday"] <= str(end_date))]

# Menyiapkan dataframe RFM
rfm_df = create_rfm_df(main_df)

# Menampilkan dashboard
st.header('Analisis RFM Sepeda')
st.subheader('RFM Summary')

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Rata-rata Recency (hari)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Rata-rata Frekuensi", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Rata-rata Monetary", value=avg_monetary)

# Visualisasi RFM
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9"]

# Visualisasi Recency
sns.barplot(y="recency", x="dteday", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Tanggal", fontsize=30)
ax[0].set_title("By Recency (hari)", loc="center", fontsize=50)

# Visualisasi Frequency
sns.barplot(y="frequency", x="dteday", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Tanggal", fontsize=30)
ax[1].set_title("By Frekuensi", loc="center", fontsize=50)

# Visualisasi Monetary
sns.barplot(y="monetary", x="dteday", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Tanggal", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)

st.pyplot(fig)

# Clustering - Manual Grouping
st.subheader('Pengelompokan Manual Penggunaan Sepeda')
# Menentukan kriteria pengelompokan
conditions = [
    (main_df['cnt'] < 100), 
    (main_df['cnt'] >= 100) & (main_df['cnt'] < 200),
    (main_df['cnt'] >= 200)
]
choices = ['Low Usage', 'Medium Usage', 'High Usage']
main_df['usage_category'] = pd.cut(main_df['cnt'], bins=[-1, 100, 200, float('inf')], labels=choices)

# Menampilkan hasil pengelompokan
st.write(main_df[['dteday', 'cnt', 'usage_category']].head())  # Menampilkan contoh hasil pengelompokan

# Visualisasi Pengelompokan
plt.figure(figsize=(10, 6))
sns.countplot(data=main_df, x='usage_category', palette='viridis')
plt.title('Jumlah Penggunaan Berdasarkan Kategori')
plt.xlabel('Kategori Penggunaan')
plt.ylabel('Jumlah')
st.pyplot(plt)

st.caption('Bike')
