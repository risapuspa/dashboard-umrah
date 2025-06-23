import streamlit as st
# ========== Page Setup ==========
st.set_page_config(
    layout="wide",
    page_title="Prediksi Umrah",
    page_icon="🕋"
)

import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns 
import os

# Membaca data dari CSV
df = pd.read_csv('DatasetUmrah.csv')  

# Bersihkan nama kolom
df.columns = df.columns.str.strip().str.lower()

# Standarkan isi kolom kategorikal
df['paket_umrah'] = df['paket_umrah'].str.strip().str.title()
df['jenis_kelamin'] = df['jenis_kelamin'].str.strip().str.title()

# Mapping harga paket
harga_paket = {
    "paket_reguler_5_bintang": "Rp41.450.000",
    "paket_plus_b": "Rp56.450.000",
    "paket_reguler_3_bintang": "Rp25.450.000",
    "paket_reguler_4_bintang": "Rp33.000.000",
    "paket_plus_a": "Rp43.450.000",
    "paket_plus_c": "Rp67.400.000"
}
# ========== Styling ==========
st.markdown("""
    <style>
    * {
        font-family: 'Times New Roman', serif !important;
    }
    html, body, [class*="css"] {
        font-size: 18px;
    }
    label {
        font-size: 1.25rem !important;
    }
    .stButton>button {
        background-color: #FFD700;
        color: black;
        font-weight: 600;
        border-radius: 8px;
        font-size: 1.1rem;
        padding: 0.6em 2.2em;
        border: none;
        display: block;
        margin: 0 auto;
    }
    .stButton>button:hover {
        background-color: #FFEA94;
    }
    .main-title {
        text-align: center;
        color: #000;
        font-size: 2.3rem;
        font-weight: bold;
        margin-bottom: 0.2em;
    }
    .sub-title {
        text-align: justify;
        font-size: 1.1rem;
        color: #333;
        margin-bottom: 1rem;
        padding: 0 4rem;
    }
    .quote {
        text-align: center;
        font-style: italic;
        color: #555;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    hr {
        border: none;
        height: 2px;
        background-color: #C8A200;
        margin-top: 10px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# ========== Header ==========
header1, header2 = st.columns([1, 16])
with header1:
    st.image("logo_babul.png", width=60)
with header2:
    st.markdown("""
    <div style='display: flex; align-items: center; height: 100%;'>
        <h1 style='color:#A62639; font-size: 28px; margin: 0;'>BABUL KA'BAH</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ========== Load Model & Label Encoders ==========
model = joblib.load('model_umrah_rf.joblib')
label_encoder = joblib.load('label_encoder_umrah.joblib')
fit_columns = joblib.load('fit_columns.joblib')

# ========== Sidebar for Method Selection ==========
st.sidebar.markdown("<h2 style='font-weight: bold;'>MENU</h2>", unsafe_allow_html=True)
sidebar_option = st.sidebar.radio(
    "Pilih Menu",
    ("Input Data Calon Jemaah Umrah", "Visualisasi Histori")
)

# ========== Form Input Manual ==========
if sidebar_option == "Input Data Calon Jemaah Umrah":
    st.markdown("<h2 class='main-title'>REKOMENDASI PAKET UMRAH</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Sistem ini dirancang untuk membantu memilih paket terbaik berdasarkan preferensi dan profil jamaah. Isi data calon jamaah untuk mendapatkan rekomendasi paket umrah yang sesuai kebutuhan.</p>", unsafe_allow_html=True)
    st.markdown("""
    <p class='quote'>
        "Dan sempurnakanlah ibadah haji dan umrah karena Allah."<br>
        – <em>QS. Al-Baqarah: 196</em>
    </p>
    """, unsafe_allow_html=True)

    # FORM
    with st.form("form_umrah"):
        form_col1, form_col2 = st.columns(2)

        with form_col1:
            jenis_kelamin = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
            usia = st.number_input("usia", min_value=18, max_value=100, value=30)
            wilayah_options = [
                "Jawa", "Sumatera", "Sulawesi", "Kalimantan", "Nusa Tenggara"
            ]
            wilayah_geografis = st.selectbox("Wilayah Geografis", wilayah_options)

        with form_col2:
            bulan_nama = [
                "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ]
            bulan_str = st.selectbox("Bulan Keberangkatan", bulan_nama)
            bulan_angka = bulan_nama.index(bulan_str) + 1

            if bulan_angka == 12:
                bulan = 0
            else:
                bulan = bulan_angka

            tanggal = st.number_input("Tanggal Keberangkatan", min_value=1, max_value=31, value=15, step=1)

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🔎 Lihat Rekomendasi")

    # ========== Prediksi ==========
    if submit:
        jk_encoded = 0 if jenis_kelamin == "Pria" else 1
        wilayah_mapping = {name: i for i, name in enumerate(wilayah_options)}
        wilayah_encoded = wilayah_mapping[wilayah_geografis]

        input_data = pd.DataFrame({
            'jenis_kelamin': [jk_encoded],
            'usia': [usia],
            'wilayah_geografis': [wilayah_encoded],
            'bulan': [bulan],
            'tanggal': [tanggal]
        })

        input_data = input_data[fit_columns]

        prediksi = model.predict(input_data)
        hasil = label_encoder.inverse_transform(prediksi)
        nama_paket = hasil[0]
        harga = harga_paket.get(nama_paket, "Rp -")

        st.success(f"Paket Umrah yang cocok untuk pelanggan ini adalah: *{nama_paket}*  \n💰 Harga: **{harga}**")

        proba = model.predict_proba(input_data)[0]
        prob_df = pd.DataFrame({
            'Paket': label_encoder.classes_,
            'Probabilitas': proba
        })
        prob_df['Harga'] = prob_df['Paket'].map(harga_paket)
        prob_df = prob_df.sort_values(by='Probabilitas', ascending=False)

        col_tabel, col_chart = st.columns([1, 1.2], gap="large")

        with col_tabel:
            st.markdown("<h4 style='margin-bottom: 0.5em;'>📊 Rincian Probabilitas:</h4>", unsafe_allow_html=True)
            st.dataframe(
                prob_df.set_index('Paket')[['Harga', 'Probabilitas']].style.format({
                    "Probabilitas": "{:.2%}"
                }),
                use_container_width=True,
                hide_index=False
            )

        with col_chart:
            st.markdown("<h4 style='margin-bottom: 0.5em;'>📈 Visualisasi Probabilitas:</h4>", unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(8.5, 4.5))
            bars = ax.bar(prob_df['Paket'], prob_df['Probabilitas'], color='#4F7942')

            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1%}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 8),
                            textcoords='offset points',
                            ha='center', va='bottom',
                            fontsize=10,
                            fontname='Times New Roman')

            ax.set_title("Visualisasi Probabilitas Paket Umrah", fontsize=14, fontweight='bold', pad=15, fontname='Times New Roman')
            ax.set_ylabel("Probabilitas", fontsize=12, fontname='Times New Roman')
            ax.set_xlabel("Nama Paket", fontsize=12, fontname='Times New Roman')
            ax.tick_params(axis='x', labelrotation=20)
            ax.grid(axis='y', linestyle='--', alpha=0.6)
            ax.set_axisbelow(True)

            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontname('Times New Roman')

            plt.tight_layout()
            st.pyplot(fig)

# ========== Visualisasi Histori ==========
elif sidebar_option == "Visualisasi Histori":
    st.markdown("<h2 style='text-align: center; font-weight: bold;'>Visualisasi Grafik Berdasarkan Data Histori</h2>", unsafe_allow_html=True)

    # Custom Legend mapping
    legend_labels = {
        0: "Paket Plus A",
        1: "Paket Plus B",
        2: "Paket Reguler 4 Bintang",
        3: "Paket Reguler 3 Bintang",
        4: "Paket Plus C",
        5: "Paket Reguler 5 Bintang"
    }

    # ===== Distribusi Paket Umrah =====
    with st.expander("Distribusi Paket Umrah"):
        df['paket_umrah_label'] = df['paket_umrah'].map(legend_labels)  
        plt.figure(figsize=(8, 6))
        sns.countplot(data=df, x='paket_umrah', palette='tab20b')

        plt.title('Distribusi Paket Umrah Desember 2022 - Februari 2024', fontsize=10)
        plt.xlabel('Jenis Paket Umrah', fontsize=9)
        plt.ylabel('Jumlah', fontsize=9)
        plt.xticks(rotation=25)
        plt.tight_layout()
        st.pyplot(plt)


    # ===== Bulan-Tahun Pemesanan =====
    with st.expander("Bulan-Tahun Pemesanan"):
   
        df['tanggal_keberangkatan'] = pd.to_datetime(df['tanggal_keberangkatan'], errors='coerce')

        df = df[df['tanggal_keberangkatan'] >= '2022-12-01']
       
        df['bulan_tahun'] = df['tanggal_keberangkatan'].dt.to_period('M').astype(str)

        # Label sumbu X (0-12 jadi bulan)
        bulan_labels = [
        "Des 2022", "Jan 2023", "Feb 2023", "Mar 2023", "Apr 2023", "Mei 2023",
        "Jun 2023", "Jul 2023", "Agu 2023", "Sep 2023", "Okt 2023", "Nov 2023", "Des 2023",
        "Jan 2024", "Feb 2024", "Mar 2024", "Apr 2024", "Mei 2024", "Jun 2024",
        "Jul 2024", "Agu 2024", "Sep 2024", "Okt 2024", "Nov 2024", "Des 2024"
    ]
        unique_bulan = df['bulan_tahun'].sort_values().unique()
        plt.figure(figsize=(8, 6))
        ax = sns.countplot(data=df, x='bulan_tahun', order=unique_bulan, color='skyblue')
        ax.set_xticklabels(unique_bulan, rotation=25)

        plt.title('Bulan-Tahun Pemesanan (Desember 2022 - Februari 2024)', fontsize=10)
        plt.xlabel('Bulan-Tahun Pemesanan', fontsize=9)
        plt.ylabel('Jumlah', fontsize=9)
        plt.tight_layout()
        st.pyplot(plt)

    # ===== Pemesanan Paket per Bulan =====
    with st.expander("Pemesanan Paket Umrah per Bulan"):

        df['tanggal_keberangkatan'] = pd.to_datetime(df['tanggal_keberangkatan'])
        df['bulan'] = df['tanggal_keberangkatan'].dt.to_period('M')

        pivot_data = df.groupby(['bulan', 'paket_umrah'])['tanggal_keberangkatan'].count().unstack().fillna(0)

            # Atur urutan bulan dari Desember 2022 sampai Februari 2024
        bulan_order = pd.period_range(start="2022-12", end="2024-02", freq="M")
        pivot_data = pivot_data.reindex(bulan_order.astype(str), fill_value=0)


        formal_colors = ['#5d7290', '#d9a066', '#a3b18a', '#c97c7c', '#f1e0c5', '#9a8f97']
        fig, ax = plt.subplots(figsize=(8, 6))
        pivot_data.plot(kind='bar', stacked=True, color=formal_colors, ax=ax)

        for container in ax.containers:
            for rect in container:
                height = rect.get_height()
                if height > 0:
                    text_color = 'white' if rect.get_facecolor()[:3] < (0.3, 0.3, 0.3) else 'black'
                    ax.text(
                        rect.get_x() + rect.get_width()/2,
                        rect.get_y() + height - (height * 0.4),
                        int(height),
                        ha='center', va='center', fontsize=8, color=text_color, fontweight='bold'
                    )

        plt.title('Pemesanan Paket Umrah per Bulan', fontsize=14)
        plt.xlabel('Bulan Pemesanan', fontsize=12)
        plt.ylabel('Jumlah Pemesanan', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        ax.legend(title='Paket Umrah', labels=[legend_labels[i] for i in range(6)], loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=3)
        st.pyplot(fig)

    # ===== Pemesanan Berdasarkan Usia =====
    with st.expander("Pemilihan Paket Berdasarkan Kelompok usia"):
       
        bins = [0, 18, 27, 37, 47, 57, 67, 77]
        labels = ["<18", "18-27", "28-37", "38-47", "48-57", "58-67", "68-77"]
        df['kelompok_usia'] = pd.cut(df['usia'], bins=bins, labels=labels, right=False)

        pivot_data = df.groupby(['kelompok_usia', 'paket_umrah']).size().unstack().fillna(0)

        formal_colors = ['#4e79a7','#f28e2b', '#76b7b2', '#e15759', '#a0cbe8',  '#ffbe7d']
        fig, ax = plt.subplots(figsize=(8, 6))
        pivot_data.plot(kind='bar', stacked=True, color=formal_colors, ax=ax, alpha=0.85)

        for container in ax.containers:
            for rect in container:
                height = rect.get_height()
                if height > 0:
                    text_color = 'white' if rect.get_facecolor()[:3] < (0.3, 0.3, 0.3) else 'black'
                    ax.text(
                        rect.get_x() + rect.get_width()/2,
                        rect.get_y() + height - (height * 0.4),
                        int(height),
                        ha='center', va='center', fontsize=7, color=text_color, fontweight='bold'
                    )

        plt.title("Pemilihan Paket Berdasarkan Kelompok usia", fontsize=12)
        plt.xlabel("Kelompok usia", fontsize=10)
        plt.ylabel("Jumlah Pemesanan", fontsize=10)
        plt.xticks(rotation=0)
        ax.legend(title='Paket Umrah', labels=[legend_labels[i] for i in range(6)], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
        st.pyplot(fig)

    # ===== Pemesanan Berdasarkan Jenis Kelamin =====
    with st.expander("Pemesanan Paket Berdasarkan Jenis Kelamin"):
     
        pivot_gender = df.groupby(['paket_umrah', 'jenis_kelamin']).size().unstack().fillna(0)

        gender_colors = ['#4e79a7', '#f3a7db']
        fig, ax = plt.subplots(figsize=(8, 6))
        pivot_gender.plot(kind='bar', color=gender_colors, ax=ax)

        plt.title("Pemesanan Paket Umrah Berdasarkan Jenis Kelamin", fontsize=12)
        plt.xlabel("Jenis Paket Umrah", fontsize=10)
        plt.ylabel("Jumlah Pemesanan", fontsize=10)
        plt.xticks(ticks=range(6), labels=[legend_labels[i] for i in range(6)], rotation=25)
        plt.legend(title="Jenis Kelamin", labels=["Pria", "Wanita"], bbox_to_anchor=(1, 1), loc='upper left')

        for container in ax.containers:
            ax.bar_label(container, fmt='%d', label_type='edge', fontsize=9, color='black', fontweight='bold')

        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig)
