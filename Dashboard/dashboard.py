import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    day_df = pd.read_csv("../Data/day.csv")  
    hour_df = pd.read_csv("../Data/hour.csv")
    
    # Data preprocessing
    day_df.drop(columns=["instant", "casual", "registered"], inplace=True)
    hour_df.drop(columns=["instant", "casual", "registered"], inplace=True)
    
    # Convert 'dteday' to datetime
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    return day_df, hour_df

day_df, hour_df = load_data()

# Filter berdasarkan tanggal
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    [day_df['dteday'].min().date(), day_df['dteday'].max().date()]
)

# Convert date_range to pandas.Timestamp
date_range = [pd.to_datetime(date) for date in date_range]

# Filter berdasarkan musim
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
day_df["season_label"] = day_df["season"].map(season_mapping)
selected_season = st.sidebar.multiselect(
    "Pilih Musim",
    options=day_df["season_label"].unique(),
    default=day_df["season_label"].unique()
)

# Filter data berdasarkan tanggal dan musim
filtered_day_df = day_df[
    (day_df['dteday'] >= date_range[0]) &
    (day_df['dteday'] <= date_range[1]) &
    (day_df["season_label"].isin(selected_season))
]

st.title("Dashboard Analisis Peminjaman Sepeda")

# Korelasi variabel numerik dengan peminjaman
st.subheader("Korelasi Variabel terhadap Jumlah Peminjaman")
correlation = filtered_day_df.select_dtypes(include=['number']).corr()["cnt"].sort_values()
st.bar_chart(correlation.drop("cnt"))

# Filter Korelasi Variabel
st.sidebar.subheader("Filter Korelasi Variabel")
selected_correlation = st.sidebar.multiselect(
    "Pilih Variabel untuk Korelasi",
    options=correlation.index.drop("cnt"),
    default=correlation.index.drop("cnt")
)

# Tampilkan korelasi yang dipilih
if selected_correlation:
    st.bar_chart(correlation[selected_correlation])

# Visualisasi peminjaman berdasarkan musim
st.subheader("Distribusi Peminjaman Berdasarkan Musim")
avg_rent_season = filtered_day_df.groupby("season_label")["cnt"].mean()
st.bar_chart(avg_rent_season)

# Peminjaman sepeda berdasarkan jam
st.subheader("Rata-rata Peminjaman Sepeda per Jam dalam Sehari")
filtered_hour_df = hour_df[
    (hour_df['dteday'] >= date_range[0]) &
    (hour_df['dteday'] <= date_range[1])
]
avg_rent_hour = filtered_hour_df.groupby("hr")["cnt"].mean()
st.bar_chart(avg_rent_hour)

# Filter Jam Peminjaman
st.sidebar.subheader("Filter Jam Peminjaman")
selected_hours = st.sidebar.multiselect(
    "Pilih Jam",
    options=avg_rent_hour.index,
    default=avg_rent_hour.index
)

# Tampilkan rata-rata peminjaman per jam yang dipilih
if selected_hours:
    st.bar_chart(avg_rent_hour[selected_hours])

# Peminjaman sepeda bulanan
st.subheader("Tren Peminjaman Sepeda Bulanan")
filtered_day_df['mnth'] = pd.to_datetime(filtered_day_df['mnth'], format='%m').dt.month
total_rent_month = filtered_day_df.groupby("mnth")["cnt"].sum()
st.line_chart(total_rent_month)

# Filter Bulan Peminjaman
st.sidebar.subheader("Filter Bulan Peminjaman")
selected_months = st.sidebar.multiselect(
    "Pilih Bulan",
    options=total_rent_month.index,
    default=total_rent_month.index
)

# Tren peminjaman bulanan yang dipilih
if selected_months:
    st.line_chart(total_rent_month[selected_months])

# Peminjaman di hari kerja vs akhir pekan
st.subheader("Perbandingan Peminjaman Sepeda pada Hari Kerja vs Akhir Pekan")
filtered_day_df["workingday_label"] = filtered_day_df["workingday"].map({0: "Akhir Pekan", 1: "Hari Kerja"})
avg_rent_workingday = filtered_day_df.groupby("workingday_label")["cnt"].mean()
st.bar_chart(avg_rent_workingday)

st.write("Copyright © 2025")