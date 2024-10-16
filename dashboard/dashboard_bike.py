import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="white")

def create_rfm_df(df):
    """Buat DataFrame RFM dari DataFrame yang diberikan."""
    # Memastikan 'cnt_y' ada dalam DataFrame
    if 'cnt_y' not in df.columns:
        st.error("Kolom 'cnt_y' tidak ada dalam DataFrame.")
        return None
    
    # Mengelompokkan berdasarkan tanggal dan hitung total penggunaan sepeda
    rfm_df = df.groupby(by=["dteday"], as_index=False).agg({
        "cnt_y": "sum"  # Total penggunaan sepeda
    })
    
    rfm_df.columns = ["dteday", "monetary"]
    
    # Mengubah 'dteday' menjadi datetime
    rfm_df["dteday"] = pd.to_datetime(rfm_df["dteday"])
    recent_date = df["dteday"].max()
    rfm_df["recency"] = (recent_date - rfm_df["dteday"]).dt.days
    
    # Menghitung frekuensi
    rfm_df["frequency"] = df.groupby("dteday")["cnt_y"].count().values
    
    return rfm_df

# Memuat data
@st.cache_data
def load_data():
    # Path relatif ke main_data.csv
    DATA_PATH = "main_data.csv"  # Perbaikan path
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

# Analisis RFM
rfm_df = create_rfm_df(filtered_df)

if rfm_df is not None:
    # Menampilkan metrik RFM
    st.subheader('Ringkasan RFM')

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

    # Memvisualisasikan RFM
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(18, 5))
    
    # Grafik Recency
    sns.barplot(y="recency", x="dteday", data=rfm_df.sort_values(by="recency", ascending=True).head(5), ax=ax[0])
    ax[0].set_title("Recency (hari)")

    # Grafik Frekuensi
    sns.barplot(y="frequency", x="dteday", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), ax=ax[1])
    ax[1].set_title("Frekuensi")

    # Grafik Monetary
    sns.barplot(y="monetary", x="dteday", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), ax=ax[2])
    ax[2].set_title("Monetary")

    st.pyplot(fig)

# Pengelompokan Manual
st.subheader('Pengelompokan Manual')

# Menambahkan penjelasan tentang pengelompokan manual
st.write("""
Pengelompokan manual dilakukan untuk mengelompokkan data penggunaan sepeda berdasarkan jumlah penggunaan per jam. Dalam analisis ini, terdapat tiga kategori berdasarkan 
jumlah penggunaan, antara lain sebagai berikut:
- **Penggunaan Rendah**: Jumlah penggunaan kurang dari 100.
- **Penggunaan Sedang**: Jumlah penggunaan antara 100 dan 200.
- **Penggunaan Tinggi**: Jumlah penggunaan lebih dari 200.\n
5 Data Awal:
""")

# Mendefinisikan kriteria pengelompokan manual
conditions = [
    (filtered_df['cnt_y'] < 100), 
    (filtered_df['cnt_y'] >= 100) & (filtered_df['cnt_y'] < 200),
    (filtered_df['cnt_y'] >= 200)
]
choices = ['Penggunaan Rendah', 'Penggunaan Sedang', 'Penggunaan Tinggi']
filtered_df['usage_category'] = pd.cut(filtered_df['cnt_y'], bins=[-1, 100, 200, float('inf')], labels=choices)

# Menampilkan hasil pengelompokan
st.write(filtered_df[['dteday', 'cnt_y', 'usage_category']].head())  # Tampilkan contoh hasil pengelompokan

# Visualisasi hasil pengelompokan
plt.figure(figsize=(10, 6))
sns.countplot(data=filtered_df, x='usage_category', palette='viridis')
plt.title('Jumlah Penggunaan Berdasarkan Kategori')
plt.xlabel('Kategori Penggunaan')
plt.ylabel('Jumlah')
st.pyplot(plt)

st.caption('Analisis Data Penggunaan Sepeda')
