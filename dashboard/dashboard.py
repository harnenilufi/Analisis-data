import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns
import plotly.express as px
import calendar


all_df = pd.read_csv("dashboard/all_data.csv")
datetime_columns = ['date']
all_df.sort_values(by='date', inplace = True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

st.image("dashboard/air-quality.png", use_container_width=True)
st.header('Konsentrasi Partikulat (PM2.5)')

col1, col2, col3, col4, col5 = st.columns(5, border=True)
col1.html(
    "<p><b>Baik</b><br>0-15.5 µg/m³</p>"
)
col2.html(
    "<p><b>Sedang</b><br>15.6-55.4 µg/m³</p>"
)
col3.html(
    "<p><b>Tidak Sehat</b><br>55.5-150.4 µg/m³</p>"
)
col4.html(
    "<p><b>Sangat Tidak Sehat</b><br>150.5-250.4 µg/m³</p>"
)
col5.html(
    "<p><b>Sedang</b><br>>250 µg/m³</p>"
)

st.subheader("Tingkat PM2.5 Setiap Tahun")
st.write(
    '''
    Informasi kualitas udara konsentrasi partikulat (PM2.5) di Kota Aotizhongxin, Changping, Guanyuan, Tiantan, Wanliu, dan Wanshouxigong.
    '''
)

all_year_df = all_df.copy()
# membuat tabel berdasarkan tahun
all_year_df['year'] = all_year_df['date'].dt.year
# grouping rata-rata tahunan PM2.5
all_year_df = all_year_df.groupby('year')['PM2.5'].mean().reset_index()
# definisi nilai maksimal rata-rata tahunan
max_pm25 = all_year_df['PM2.5'].max()
# memberikan warna pada nilai maksimal
all_year_df['color'] = all_year_df['PM2.5'].apply(
    lambda x: 'red' if x == max_pm25 else '#D3D3D3'
)

with st.container():
    # membuat bar
    fig = px.bar(
        all_year_df,
        x='year',
        y='PM2.5',
        color= 'color',
        text=all_year_df['PM2.5'].round(1),
        color_discrete_map = 'identity'
    )

    fig.update_layout(
        xaxis_title = 'Tahun',
        yaxis_title = 'Rata-rata PM2.5',
        plot_bgcolor = 'white'
    )
    # Menambahkan line chart
    fig.add_scatter(
        x=all_year_df['year'],
        y=all_year_df['PM2.5'],
        mode='lines+markers', # menambahkan titik dan marker pada line chart
        name='Tren PM2.5',
        line=dict(color='blue', width=2, dash='dash')
    )
st.plotly_chart(fig)

with st.expander("See Explanation"):
    st.write(
        """
        Kualitas udara dalam rentang tahun 2013-2017 pling buruk terjadai pada tahun 2017.  
        Dimana tingkat rata-rata PM2.5 di tahun tersebut mencapai 94.5.  
        Setelah penurunan tingkat PM2.5 di 2 tahun terakhir yaitu tahun 2015 dan 2016, 
        peningkatan signifikan terjadi pada tahun 2017
        """
    )
# kategori kualitas udara sesuai dengan PM2.5, standar yang digunakan adalah BMKG
def categorize_pm25(pm25):
    if pm25 <= 15.5:
        return 'Baik'
    elif pm25 <= 55.4:
        return 'Sedang'
    elif pm25 <= 150.4:
        return 'Tidak Sehat'
    elif pm25 <= 250.4:
        return 'Sangat Tidak Sehat'
    else:
        return 'Berbahaya'

# menkategorikan warna sesuai tingkat kualitas udara
colors_kategori = {
    'Baik': "#5CB338", #hijau
    'Sedang': '#B4EBE6', #biru muda
    'Tidak Sehat': "#FFC145", #orange
    'Sangat Tidak Sehat': '#FB4141', #merah
    'Berbahaya': '#A5158C' #ungu
    
}

st.subheader("Best Air Quality Ranking")

with st.container():
    # Membuat average PM2.5 sesuai sesuai dengan station
    station_avgpm25_df = all_df.groupby('station')['PM2.5'].mean().reset_index()
    # Mengurutkan sesuai dengan nilai rata-rata paling kecil
    station_avgpm25_df = station_avgpm25_df.sort_values(by='PM2.5', ascending=False)
    # memberikan label data sesuai dengan tingkat PM2.5
    station_avgpm25_df['kategori'] = station_avgpm25_df['PM2.5'].apply(categorize_pm25)

    # maping warna sesuai dengan kategori udara
    colors = station_avgpm25_df['kategori'].map(colors_kategori)

    # membuat barh
    fig = plt.figure(figsize=(10, 6))
    bars = plt.barh(
        station_avgpm25_df['station'],
        station_avgpm25_df['PM2.5'],
        color=colors
    )


    for bar, category in zip(bars, station_avgpm25_df['kategori']):
        width = bar.get_width()
        plt.text(
            0.5,
            bar.get_y() + bar.get_height()/2,
            f'{width:.1f} ({category})',
            va='center'
        )
    plt.xlabel('Rata-rata PM2.5')
    plt.ylabel('Kota')
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    legend_elements = [Patch(facecolor=color, label=label) for label, color in colors_kategori.items()]
    plt.legend(handles=legend_elements, title='Kategori Kualitas Udara', bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

st.subheader("Kualitas Udara Rata-Rata setiap Bulan")
st.write(
    '''
    Menampilkan kualitas udara di seluruh kota.
    '''
)
df_bulan = all_df.copy()
df_bulan['month'] = df_bulan['date'].dt.month

# Membuat average bulanan PM2.5
avg_pm25_per_month = df_bulan.groupby('month')['PM2.5'].mean().reset_index()

# Definine bulan dengan kualitas udara terbaik
best_month = avg_pm25_per_month.loc[avg_pm25_per_month['PM2.5'].idxmin()]

bulan_nama = calendar.month_name[int(best_month['month'])]

# Membuat bar chart berdasarka rata-rata bulanan
fig, ax = plt.subplots(figsize=(10,6))
bars = ax.bar(
    avg_pm25_per_month['month'],
    avg_pm25_per_month['PM2.5'],
    color=['green' if m == best_month['month'] else '#A9CCE3' for m in avg_pm25_per_month['month']]
)

# Memberikan nama setiap titik pada garis x
ax.set_xticks(
    avg_pm25_per_month['month'],
    [calendar.month_name[m] for m in avg_pm25_per_month['month']],
    rotation=45
)

# Membarikan nilai rata-rata disetiap bulan
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        height + 0.5,
        f'{height:.1f}',
        ha='center')

ax.set_title('Rata-rata PM2.5 per Bulan')
ax.set_xlabel('Bulan')
ax.set_ylabel('Rata-rata PM2.5')
ax.grid(axis='y', linestyle='--', alpha=0.5)

st.pyplot(fig)
select, data = st.columns ([1, 3])

with select:
    st.markdown(
        '<h5 style= "text-align:center">Pilih Kota:</6>'
        , unsafe_allow_html=True)
    sb = st.selectbox('Pilihan Kota:', ['Aotizhongxin', 'Changping', 'Guanyuan', 'Tiantan', 'Wanliu', 'Wanshouxigong'])

with data:
    # Membuat data average sesuai dengan stasiun disetiap bulan
    avg_pm25_per_city_month = df_bulan.groupby(['station', 'month'])['PM2.5'].mean().reset_index()
    # membuat kategori sesuai dengan tingkat kualitas PM2.5
    avg_pm25_per_city_month['kategori'] = avg_pm25_per_city_month['PM2.5'].apply(categorize_pm25)

    # Looping membuat bar chart disetiap station
    df_station = avg_pm25_per_city_month[avg_pm25_per_city_month['station'] == sb]
    # maping warna
    colors = df_station['kategori'].map(colors_kategori)
    
    # membuat bar chart perbulan disetiap station
    fig, ax = plt.subplots(figsize=(10,6))
    bars = ax.bar(
        df_station['month'],
        df_station['PM2.5'],
        color=colors
    )

    # Label Bulan
    ax.set_xticks(df_station['month'])
    ax.set_xticklabels(
        [calendar.month_name[m] for m in df_station['month']],
        rotation=45
    )
    ax.set_title(f'Rata-rata PM2.5 per Bulan di {sb}')
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Rata-rata PM2.5')
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    # Tambah label nilai di atas bar
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2,
            height + 0.5,
            f'{height:.1f}',
            ha='center'
        )
    
    # Memberikan keterangan kategori
    legend_elements = [Patch(facecolor=color, label=label) for label, color in colors_kategori.items()]
    plt.legend(handles=legend_elements, title='Kategori Kualitas Udara', bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)
