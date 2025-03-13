import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    day_df = pd.read_csv("day.csv")
    hour_df = pd.read_csv("hour.csv")
    
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
    [day_df['dteday'].min(), day_df['dteday'].max()]
)

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
    (day_df['dteday'] >= pd.to_datetime(date_range[0])) &
    (day_df['dteday'] <= pd.to_datetime(date_range[1])) &
    (day_df['season_label'].isin(selected_season))
]

st.title("Dashboard Analisis Peminjaman Sepeda")

# Korelasi variabel numerik dengan peminjaman
st.subheader("Korelasi Variabel terhadap Jumlah Peminjaman")
correlation = day_df.select_dtypes(include=['number']).corr()["cnt"].sort_values()
st.bar_chart(correlation.drop("cnt"))

# Visualisasi peminjaman berdasarkan musim
st.subheader("Distribusi Peminjaman Berdasarkan Musim")
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
day_df["season_label"] = day_df["season"].map(season_mapping)
avg_rent_season = day_df.groupby("season_label")["cnt"].mean()
st.bar_chart(avg_rent_season)

# Peminjaman sepeda berdasarkan jam
st.subheader("Rata-rata Peminjaman Sepeda per Jam dalam Sehari")
avg_rent_hour = hour_df.groupby("hr")["cnt"].mean()
st.bar_chart(avg_rent_hour)

# Peminjaman sepeda bulanan
st.subheader("Tren Peminjaman Sepeda Bulanan")
day_df['mnth'] = pd.to_datetime(day_df['mnth'], format='%m').dt.month
total_rent_month = day_df.groupby("mnth")["cnt"].sum()
st.line_chart(total_rent_month)

# Peminjaman di hari kerja vs akhir pekan
st.subheader("Perbandingan Peminjaman Sepeda pada Hari Kerja vs Akhir Pekan")
day_df["workingday_label"] = day_df["workingday"].map({0: "Akhir Pekan", 1: "Hari Kerja"})
avg_rent_workingday = day_df.groupby("workingday_label")["cnt"].mean()
st.bar_chart(avg_rent_workingday)

# Sidebar untuk clustering
st.sidebar.header("Clustering Options")
n_clusters = st.sidebar.slider("Jumlah Cluster", min_value=2, max_value=10, value=4)

# Pilih fitur untuk clustering
features = st.sidebar.multiselect(
    "Pilih Fitur untuk Clustering",
    options=["temp", "hum", "windspeed", "cnt"],
    default=["temp", "cnt"]
)

# Filter data untuk clustering
if features:
    clustering_data = day_df[features]
    
    # Lakukan clustering dengan K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    day_df['cluster'] = kmeans.fit_predict(clustering_data)
    
    # Visualisasi hasil clustering
    st.subheader("Hasil Clustering")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        x=features[0],
        y=features[1],
        hue=day_df['cluster'],
        palette="viridis",
        data=day_df,
        ax=ax
    )
    ax.set_title(f"Clustering Berdasarkan {features[0]} dan {features[1]}")
    st.pyplot(fig)
    
    # Tampilkan deskripsi cluster
    st.subheader("Deskripsi Cluster")
    cluster_summary = day_df.groupby('cluster')[features].mean()
    st.write(cluster_summary)
else:
    st.warning("Silakan pilih setidaknya dua fitur untuk melakukan clustering.")

st.write("Copyright © 2025")