import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# --- Konfigurasi Halaman Website ---
st.set_page_config(page_title="Proyek Analisis Data - Bike Sharing", layout="wide")

# --- Helper Functions (Untuk Menyiapkan Data Frame) ---
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    return daily_orders_df

def create_hourly_trend_df(df):
    return df.groupby(['hr', 'workingday_str'])['cnt'].mean().reset_index()

def create_by_season_df(df):
    return df.groupby('season_label')['cnt'].mean().reset_index()

def create_by_weather_df(df):
    return df.groupby('weather_label')['cnt'].mean().reset_index()

def create_by_time_category_df(df):
    time_order = ['Morning (05-11)', 'Afternoon (11-15)', 'Evening (15-20)', 'Night (20-05)']
    # Pastikan hanya kategori yang ada di data yang diambil
    df_grouped = df.groupby('time_category')['cnt'].mean().reindex(time_order)
    return df_grouped.reset_index()

# --- Load Data ---
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'main_data.csv')
all_df = pd.read_csv(file_path)

# Pastikan dteday bertipe datetime
all_df["dteday"] = pd.to_datetime(all_df["dteday"])
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)

# --- Sidebar (Filter) ---
with st.sidebar:
    st.markdown(
        """
        <div style="
            background-color: #F0F2F6; 
            padding: 20px; 
            border-radius: 20px; 
            border: 2px solid #d1d5db; 
            text-align: center;
            margin-bottom: 20px;
        ">
            <h1 style="
                color: #FF4B4B; 
                font-size: 32px; 
                margin: 0;
            ">
                🚲 <br>Bike Sharing
            </h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.header("Filter Rentang Waktu")
    
    min_date = all_df["dteday"].min()
    max_date = all_df["dteday"].max()
    
    try:
        start_date, end_date = st.date_input(
            label='Pilih Tanggal',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except ValueError:
        st.error("Mohon pilih rentang tanggal yang valid.")
        st.stop()
        
# Filter data utama
main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                 (all_df["dteday"] <= str(end_date))]

# Menyiapkan DataFrame untuk visualisasi
daily_orders_df = create_daily_orders_df(main_df)
hourly_trend_df = create_hourly_trend_df(main_df)
season_df = create_by_season_df(main_df)
weather_df = create_by_weather_df(main_df)
time_cat_df = create_by_time_category_df(main_df)

# --- HEADER DASHBOARD ---
st.title("🚲 Proyek Analisis Data: Bike Sharing Dataset")
st.markdown("""
**Nama:** Agil Firli Gunawan  
**Email:** agilfirli29@gmail.com  
**ID Dicoding:** Agil Firli Gunawan
""")

st.markdown("---")

# --- BAGIAN 1: PERTANYAAN BISNIS ---
st.header("Pertanyaan Bisnis")
st.markdown("""
Pertanyaan utama yang ingin dijawab melalui dashboard ini:
1. **Bagaimana pola penyewaan sepeda berdasarkan waktu (jam) dalam sehari?** Apakah ada perbedaan aktivitas antara hari kerja (*Working Day*) dan hari libur (*Holiday*)?
2. **Bagaimana pengaruh musim dan kondisi cuaca terhadap rata-rata penyewaan sepeda?** Kondisi apa yang paling disukai pengguna?
""")
st.markdown("---")

# --- BAGIAN 2: OVERVIEW HARIAN ---
st.header("Daily Dashboard Overview")
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = daily_orders_df.cnt.sum()
    st.metric("Total Penyewaan", value=f"{total_orders:,}")

with col2:
    avg_orders = daily_orders_df.cnt.mean()
    st.metric("Rata-rata Harian", value=f"{avg_orders:.0f}")

with col3:
    max_orders = daily_orders_df.cnt.max()
    st.metric("Penyewaan Tertinggi", value=f"{max_orders:,}")

# Grafik Garis Harian
fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(daily_orders_df["dteday"], daily_orders_df["cnt"], linewidth=2, color="#90CAF9")
ax.set_title("Tren Jumlah Penyewaan Harian", fontsize=20)
ax.set_xlabel(None)
ax.set_ylabel("Jumlah Sewa")
st.pyplot(fig)

st.markdown("---")

# --- BAGIAN 3: ANALISIS PERTANYAAN 1 (POLA WAKTU) ---
st.header("Analisis Pola Waktu (Jam & Hari)")
st.subheader("Pola Penyewaan: Hari Kerja vs Hari Libur")

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x='hr', y='cnt', hue='workingday_str', 
    data=hourly_trend_df, palette='bright', 
    marker='o', ax=ax
)
ax.set_title("Rata-rata Penyewaan per Jam", fontsize=15)
ax.set_xlabel("Jam (0-23)")
ax.set_ylabel("Rata-rata Sewa")
ax.set_xticks(range(0, 24))
ax.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig)

# INSIGHT MENGGUNAKAN EXPANDER
with st.expander("💡 Lihat Insight Analisis Pola Waktu"):
    st.markdown("""
    **Insight:**
    1. **Pola Hari Kerja (Commuting):**
       - Terlihat pola **"Bimodal"** (dua puncak) yang tajam pada pukul **08:00 pagi** dan **17:00 sore**.
       - Ini mengindikasikan sepeda digunakan sebagai alat transportasi untuk berangkat dan pulang kerja/sekolah.
    2. **Pola Hari Libur (Rekreasi):**
       - Pola kurva lebih landai (**"Unimodal"**) dengan puncak aktivitas terjadi di siang hari (**12:00 - 15:00**).
       - Ini menandakan penggunaan untuk tujuan santai atau olahraga.
    """)

st.markdown("---")

# --- BAGIAN 4: ANALISIS PERTANYAAN 2 (MUSIM & CUACA) ---
st.header("Analisis Faktor Lingkungan (Musim & Cuaca)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pengaruh Musim")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        x='season_label', y='cnt', data=season_df, 
        palette='viridis', ax=ax
    )
    ax.set_xlabel(None)
    ax.set_ylabel("Rata-rata Sewa")
    st.pyplot(fig)

with col2:
    st.subheader("Pengaruh Cuaca")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        x='weather_label', y='cnt', data=weather_df, 
        palette='coolwarm', ax=ax
    )
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    st.pyplot(fig)

# INSIGHT MENGGUNAKAN EXPANDER
with st.expander("💡 Lihat Insight Analisis Lingkungan"):
    st.markdown("""
    **Insight:**
    1. **Musim:** Penyewaan tertinggi terjadi pada musim **Gugur (Fall)**, diikuti oleh Panas (Summer). Musim Semi (Spring) memiliki rata-rata terendah, kemungkinan karena cuaca transisi yang belum stabil.
    2. **Cuaca:** Pengguna sangat menyukai cuaca **Cerah/Berawan**. Terjadi penurunan drastis saat hujan atau salju, yang menunjukkan pengguna sangat memprioritaskan kenyamanan dan keselamatan.
    """)

st.markdown("---")

# --- BAGIAN 5: ANALISIS LANJUTAN (CLUSTERING WAKTU) ---
st.header("Analisis Lanjutan: Kategori Waktu")
st.markdown("Mengelompokkan jam menjadi kategori: Morning, Afternoon, Evening, dan Night.")

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(
    x='time_category', y='cnt', data=time_cat_df, 
    palette='pastel', ax=ax
)
ax.set_title("Rata-rata Penyewaan Berdasarkan Kategori Waktu")
ax.set_xlabel(None)
st.pyplot(fig)

with st.expander("💡 Lihat Insight Analisis Lanjutan"):
    st.markdown("""
    Hasil *binning* menunjukkan bahwa kategori waktu **Evening (15:00 - 20:00)** memiliki rata-rata penyewaan tertinggi. Hal ini sejalan dengan temuan jam sibuk pulang kerja.
    """)

st.markdown("---")

# --- BAGIAN 6: CONCLUSION ---
st.header("Conclusion (Kesimpulan Akhir)")
st.markdown("""
Berdasarkan seluruh analisis yang telah dilakukan, berikut adalah kesimpulan untuk menjawab pertanyaan bisnis:

1.  **Pola Waktu:** Penyewaan sepeda sangat bergantung pada jenis hari. Pada **Hari Kerja**, sepeda digunakan untuk mobilitas (puncak jam 8 pagi & 5 sore). Pada **Hari Libur**, sepeda digunakan untuk rekreasi (puncak siang hari).
    
2.  **Faktor Lingkungan:** Cuaca dan musim adalah faktor krusial. Bisnis penyewaan sepeda sangat bergantung pada cuaca cerah dan musim yang hangat (Gugur/Panas). Strategi promosi sebaiknya digencarkan saat prakiraan cuaca cerah.
""")

st.caption("Copyright © Dicoding 2026 - Agil Firli Gunawan")