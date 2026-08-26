import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

st.set_page_config(page_title="Dashboard Bike Sharing", layout="wide")
sns.set(style="white")

WEATHER_LABELS = {1: 'Cerah', 2: 'Mendung', 3: 'Hujan'}
DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
DAY_LABELS_ID = {
    'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
    'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
}


# ================= Fungsi Pertanyaan 1: Penggunaan Sepeda terhadap Kondisi Cuaca =================
def weather_impact(df):
    weather_avg = df.groupby('weathersit_x')['cnt_x'].mean().reindex([1, 2, 3])

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x='weathersit_x', y='cnt_x', order=[1, 2, 3], ax=ax)
    ax.set_title('Distribusi Penggunaan Sepeda Berdasarkan Kondisi Cuaca')
    ax.set_xlabel('Kondisi Cuaca')
    ax.set_ylabel('Rata-Rata Penggunaan Sepeda')
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Cerah', 'Mendung', 'Hujan'])
    st.pyplot(fig)
    plt.close(fig)

    # --- Insight dihitung ulang dari data yang sedang difilter, bukan teks tetap ---
    if weather_avg.dropna().empty:
        st.info("Tidak ada data cuaca pada rentang tanggal yang dipilih.")
        return

    best_code = weather_avg.idxmax()
    worst_code = weather_avg.idxmin()
    best_label = WEATHER_LABELS.get(best_code, '-')
    worst_label = WEATHER_LABELS.get(worst_code, '-')

    st.write(
        f"Pada rentang tanggal yang dipilih, penggunaan sepeda **paling tinggi** terjadi saat cuaca "
        f"**{best_label}** (rata-rata {weather_avg[best_code]:,.0f} sepeda), dan **paling rendah** saat "
        f"cuaca **{worst_label}** (rata-rata {weather_avg[worst_code]:,.0f} sepeda)."
    )


# ================= Fungsi Pertanyaan 2: Penggunaan Sepeda per Hari dalam Satu Pekan =================
def usage_by_day_of_week(df):
    # Setiap baris cnt_x berulang untuk tiap jam (data hasil merge harian+jam),
    # jadi diringkas dulu per tanggal sebelum dirata-ratakan per hari.
    daily_usage = df.drop_duplicates(subset='dteday')[['dteday', 'cnt_x']].copy()
    daily_usage['day_of_week'] = daily_usage['dteday'].dt.day_name()
    weekly_usage = daily_usage.groupby('day_of_week')['cnt_x'].mean().reindex(DAY_ORDER)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=[DAY_LABELS_ID[d] for d in DAY_ORDER], y=weekly_usage.values, ax=ax)
    ax.set_title('Rata-Rata Penggunaan Sepeda per Hari dalam Satu Pekan')
    ax.set_xlabel('Hari dalam Satu Pekan')
    ax.set_ylabel('Rata-Rata Penggunaan Sepeda')
    st.pyplot(fig)
    plt.close(fig)

    if weekly_usage.dropna().empty:
        st.info("Tidak ada data yang cukup pada rentang tanggal yang dipilih.")
        return

    busiest_en = weekly_usage.idxmax()
    quietest_en = weekly_usage.idxmin()
    busiest_id = DAY_LABELS_ID[busiest_en]
    quietest_id = DAY_LABELS_ID[quietest_en]

    st.write(
        f"Pada rentang tanggal yang dipilih, hari dengan penggunaan sepeda **tertinggi** adalah "
        f"**{busiest_id}** (rata-rata {weekly_usage[busiest_en]:,.0f} sepeda/hari), sedangkan yang "
        f"**terendah** adalah **{quietest_id}** (rata-rata {weekly_usage[quietest_en]:,.0f} sepeda/hari)."
    )


# ================= Memuat Data =================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(base_dir, "main_data.csv")
    df = pd.read_csv(DATA_PATH)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df


all_df = load_data()
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

# ================= Sidebar =================
with st.sidebar:
    st.title("🚲 Bike Sharing Dashboard")
    st.markdown(
        "Gunakan filter di bawah untuk memilih **rentang tanggal**. "
        "Semua grafik dan kesimpulan di halaman utama akan otomatis "
        "menyesuaikan dengan rentang yang kamu pilih."
    )
    date_range = st.date_input(
        label='Pilih Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    st.caption("Klik tanggal awal lalu tanggal akhir untuk memilih rentang.")

# Tangani kasus saat user baru memilih satu tanggal (belum lengkap dua tanggal)
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    st.warning("Pilih tanggal **awal dan akhir** pada sidebar untuk menampilkan data.")
    st.stop()

filtered_df = all_df[
    (all_df["dteday"] >= pd.to_datetime(start_date)) &
    (all_df["dteday"] <= pd.to_datetime(end_date))
]

# ================= Header & Konteks =================
st.header('Dashboard Bike Sharing')
st.caption(f"Menampilkan data dari **{start_date}** sampai **{end_date}**")

if filtered_df.empty:
    st.warning("Tidak ada data pada rentang tanggal yang dipilih. Coba perlebar rentang tanggal di sidebar.")
    st.stop()

# Ringkasan angka (KPI) supaya user langsung dapat gambaran sebelum lihat grafik
daily_totals = filtered_df.drop_duplicates(subset='dteday')['cnt_x']
col1, col2, col3 = st.columns(3)
col1.metric("Total Penggunaan", f"{daily_totals.sum():,.0f}")
col2.metric("Rata-Rata Harian", f"{daily_totals.mean():,.0f}")
col3.metric("Jumlah Hari", f"{daily_totals.shape[0]}")

st.divider()

# ================= Grafik & Insight =================
st.subheader('Data Penggunaan Sepeda Terhadap Kondisi Cuaca')
weather_impact(filtered_df)

st.subheader('Penggunaan Sepeda Berdasarkan Hari dalam Satu Pekan')
usage_by_day_of_week(filtered_df)

st.caption('Analisis Data Penggunaan Sepeda -- M. Farid Saputra')