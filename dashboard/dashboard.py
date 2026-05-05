import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
import numpy as np

# Konfigurasi Halaman
st.set_page_config(
    page_title="Bike Sharing Dashboard 🚲",
    page_icon="🚲",
    layout="wide"
)

# Fungsi Memuat Data
base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "data_bersih.csv")

data_bersih = pd.read_csv(file_path)

# Konversi tanggal
data_bersih['dteday'] = pd.to_datetime(data_bersih['dteday'])



with st.sidebar:
    st.title("Filter Dashboard")
    
    # Filter Rentang Waktu
    min_date = data_bersih ["dteday"].min()
    max_date = data_bersih["dteday"].max()
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Filter Musim (Multiselect)
    list_musim = data_bersih['season_name'].unique()
    selected_season = st.multiselect(
        "Filter Berdasarkan Musim:",
        options=list_musim,
        default=list_musim
    )

# Menerapkan Filter ke Dataframe
main_df = data_bersih[
    (data_bersih["dteday"] >= str(start_date)) & 
    (data_bersih["dteday"] <= str(end_date)) &
    (data_bersih["season_name"].isin(selected_season))
]


st.title('🚲 Dashboard Analisis Data Bike Sharing')
st.markdown(f"Statistik penyewaan dari **{start_date}** sampai **{end_date}**")

# Metrics Utama
col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = main_df['cnt'].sum()
    st.metric("Total Penyewaan", value=f"{total_rentals:,}")
with col2:
    total_reg = main_df['registered'].sum()
    st.metric("Pengguna Terdaftar", value=f"{total_reg:,}")
with col3:
    total_cas = main_df['casual'].sum()
    st.metric("Pengguna Biasa (Casual)", value=f"{total_cas:,}")

st.divider()

# fitur
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Analisis Musim", 
    "🌡️ Analisis Cuaca & Suhu", 
    "👥 Tipe Pengguna", 
    "📑 Data Interaktif"
])

with tab1:
    st.subheader("Analisis Distribusi Penyewaan Berdasarkan Musim")
    
    
    if main_df.empty:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih. Silakan sesuaikan rentang waktu atau musim di sidebar.")
    else:
        col_left, col_right = st.columns(2)
        
        
        category_order = ['Winter', 'Spring', 'Summer', 'Fall']
        actual_order = [m for m in category_order if m in selected_season]
        
      
        with col_left:
            fig1, ax1 = plt.subplots(figsize=(6, 6))
            sns.barplot(
                x='season_name', 
                y='cnt', 
                data=main_df, 
                order=actual_order, # Gunakan urutan yang sudah difilter
                color='steelblue', 
                ax=ax1
            )
            ax1.set_title("Distribusi Jumlah Sewa (Bar)", fontsize=12)
            ax1.set_xlabel("Season")
            ax1.set_ylabel("Jumlah Sewa Sepeda (cnt)")
            st.pyplot(fig1)

       
        with col_right:
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            
            # Agregasi data
            pie_data = main_df.groupby('season_name')['cnt'].sum()
            pie_data = pie_data.reindex(actual_order).dropna()
            
            if not pie_data.empty and pie_data.sum() > 0:
                ax2.pie(
                    pie_data, 
                    labels=pie_data.index, 
                    autopct='%1.1f%%', 
                    startangle=90,
                    colors=sns.color_palette('tab10')
                )
                ax2.set_title("Distribusi Proporsi Sewa (Pie)", fontsize=12)
                st.pyplot(fig2)
            else:
                st.write("Data tidak cukup untuk menampilkan Pie Chart.")
    
    with st.expander("Lihat Penjelasan"):
        st.write("Visualisasi ini membandingkan rata-rata penyewaan dan kontribusi total tiap musim.")

with tab2:
    st.subheader("Analisis Pengaruh Suhu terhadap Penyewaan")
    
    
    if main_df.empty:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        
        col_left, col_right = st.columns(2)
        
        
        with col_left:
            fig1, ax1 = plt.subplots(figsize=(6, 6)) 
            
            # Mengambil sampel data agar plot tidak berat
            sample_df = main_df.sample(min(len(main_df), 1000), random_state=42)
            
            # Plot Regresi (Gambar Kiri)
            sns.regplot(
                x='atemp', 
                y='cnt', 
                data=sample_df, 
                scatter_kws={'alpha':0.3}, 
                line_kws={'color':'red'}, 
                ax=ax1
            )
            
            # Pengaturan Label Kolom Kiri
            ax1.set_title("Korelasi Suhu vs Penyewaan", fontsize=12)
            ax1.set_xlabel("Suhu yang Dirasakan (atemp)")
            ax1.set_ylabel("Jumlah Sewa")
            st.pyplot(fig1)

        
        with col_right:
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            
            
            temp_df = main_df.copy()
            temp_df['atemp_round'] = temp_df['atemp'].round()
            temp_grouped = temp_df.groupby('atemp_round')['cnt'].mean().reset_index()
            
            
            ax2.plot(
                temp_grouped['atemp_round'], 
                temp_grouped['cnt'], 
                marker='o',          
                linestyle='-',       
                linewidth=2,
                color='tab:blue'     
            )
            
            # Pengaturan Label Kolom Kanan
            ax2.set_title("Rata-rata Sewa Berdasarkan Suhu", fontsize=12)
            ax2.set_xlabel("Suhu yang Dirasakan (atemp) (°C)")
            ax2.set_ylabel("Rata-rata Jumlah Sewa Sepeda (cnt)")
            ax2.grid(True, linestyle='--', alpha=0.7) # Menambahkan grid agar mirip gambar
            
            st.pyplot(fig2)
            
        # Pesan Info di bawah kedua chart
        st.info("💡 **Kesimpulan Berdampingan:** Kolom kiri menunjukkan korelasi positif yang jelas (semakin hangat semakin ramai). Kolom kanan mempertegas tren tersebut dengan menunjukkan nilai rata-rata, di mana puncak penyewaan terjadi pada rentang suhu hangat sekitar 25°C - 35°C.")

with tab3:
    st.subheader("Tren dan Perbandingan Tipe Pengguna")
    
    if main_df.empty:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        
        monthly_rentals = main_df.groupby(main_df['dteday'].dt.to_period('M')).agg({
            'registered': 'sum',
            'casual': 'sum'
        }).reset_index()
        monthly_rentals['date'] = monthly_rentals['dteday'].dt.to_timestamp()

        fig_trend, ax_trend = plt.subplots(figsize=(14, 7))
        ax_trend.plot(monthly_rentals['date'], monthly_rentals['registered'], marker='o', label='Registered Rentals', linewidth=2)
        ax_trend.plot(monthly_rentals['date'], monthly_rentals['casual'], marker='o', label='Casual Rentals', linewidth=2)

        ax_trend.set_title('Monthly Bike Rentals: Registered vs Casual', fontsize=16)
        ax_trend.set_xlabel('Month')
        ax_trend.set_ylabel('Total Customers')
        ax_trend.legend()
        ax_trend.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        
        st.pyplot(fig_trend)
        
        st.divider() 

        
        col_left, col_right = st.columns(2)
        
        # Kolom Kiri: Stacked Bar Chart per Musim
        with col_left:
            fig1, ax1 = plt.subplots(figsize=(6, 7))
            category_order = ['Winter', 'Spring', 'Summer', 'Fall']
        
            actual_order = [m for m in category_order if m in selected_season]
            
            user_type_df = main_df.groupby('season_name')[['registered', 'casual']].sum().reindex(actual_order).reset_index()
            
            ax1.bar(user_type_df['season_name'], user_type_df['registered'], label='Registered', color='#4CAF50')
            ax1.bar(user_type_df['season_name'], user_type_df['casual'], bottom=user_type_df['registered'], label='Casual', color='#FF5722')
            
            ax1.set_title("Total Sewa per Musim", fontsize=12)
            ax1.legend()
            st.pyplot(fig1)

        # Kolom Kanan: Pie Chart Proporsi Total
        with col_right:
            fig2, ax2 = plt.subplots(figsize=(6, 7))
            total_reg = main_df['registered'].sum()
            total_cas = main_df['casual'].sum()
            
            if (total_reg + total_cas) > 0:
                ax2.pie(
                    [total_reg, total_cas], 
                    labels=['Registered', 'Casual'], 
                    autopct='%1.1f%%', 
                    startangle=140, 
                    colors=['#4CAF50', '#FF5722']
                )
                ax2.set_title("Proporsi Total Pengguna", fontsize=12)
                st.pyplot(fig2)
            else:
                st.write("Data tidak mencukupi.")

    with st.expander("Lihat Penjelasan"):
        st.write("""
        1. **Line Chart**: Menunjukkan fluktuasi penyewaan setiap bulan. Terlihat adanya pola musiman di mana penyewaan meningkat drastis di pertengahan tahun.
        2. **Stacked Bar**: Memperlihatkan bahwa dominasi pengguna Registered terjadi di semua musim.
        3. **Pie Chart**: Memberikan gambaran besar bahwa mayoritas pengguna adalah mereka yang sudah terdaftar.
        """)

with tab4:
    st.subheader("Eksplorasi Lanjutan: Heatmap Jam & Hari")
    
    if main_df.empty:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        
        heatmap_data = main_df.copy()
        
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        try:
            pivot_df = heatmap_data.pivot_table(
                index='weekday', 
                columns='hr', 
                values='cnt', 
                aggfunc='sum'
            ).reindex(day_order)

            fig_heat, ax_heat = plt.subplots(figsize=(12, 7))
            sns.heatmap(
                pivot_df, 
                cmap='coolwarm', 
                annot=False, 
                ax=ax_heat,
                cbar_kws={'label': 'Total Sewa'}
            )
            
            ax_heat.set_title('Bike Rentals Heatmap by Weekday and Hour', fontsize=15)
            ax_heat.set_xlabel('Hour of the Day')
            ax_heat.set_ylabel('Day of the Week')
            
            st.pyplot(fig_heat)
            st.info("💡 **Insight:** Area merah menunjukkan waktu tersibuk. Perhatikan perbedaan pola antara hari kerja (jam masuk/pulang kantor) dan akhir pekan (siang hari).")
            
        except Exception as e:
            st.error(f"Gagal memuat Heatmap. Pastikan kolom 'hr' dan 'weekday_name' tersedia di dataset. Error: {e}")

    st.divider()

    
    st.subheader("Tabel Data Interaktif")
    st.markdown("Gunakan tabel di bawah ini untuk melihat detail data yang telah difilter.")
    st.dataframe(main_df, use_container_width=True)
    
    # Fitur download
    csv = main_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Data Terfilter (CSV)",
        data=csv,
        file_name='bike_sharing_filtered.csv',
        mime='text/csv',
    )

# Footer
st.divider()
st.caption('Dashboard created by Dika Della And Dwi (DDD) | Bisnis Intelegen Project 2026')
