import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ========== Load Model & Label Encoders ========== 
try:
    model = joblib.load('model_umrah_rf.joblib')
    label_encoder = joblib.load('label_encoder_umrah.joblib')
    fit_columns = joblib.load('fit_columns.joblib')
except Exception as e:
    st.error(f"Gagal memuat model atau encoder: {e}")
    st.stop()

# ========== Harga Paket Mapping ========== 
harga_paket = {
    "paket_reguler_5_bintang": "Rp41.450.000",
    "paket_plus_b": "Rp56.450.000",
    "paket_reguler_3_bintang": "Rp25.450.000",
    "paket_reguler_4_bintang": "Rp33.000.000",
    "paket_plus_a": "Rp43.450.000",
    "paket_plus_c": "Rp67.400.000"
}

# ========== Page Setup & Style ========== 
st.set_page_config(layout="wide", page_title="Prediksi Umrah", page_icon="🕋")
st.markdown(""" 
    <style>
    * { font-family: 'Times New Roman', serif !important; }
    html, body, [class*="css"] { font-size: 18px; }
    .stButton>button {
        background-color: #FFD700; color: black; font-weight: 600; border-radius: 8px;
        font-size: 1.1rem; padding: 0.6em 2.2em; border: none; display: block; margin: 0 auto;
    }
    .stButton>button:hover { background-color: #FFEA94; }
    .main-title { text-align: center; color: #000; font-size: 2.3rem; font-weight: bold; margin-bottom: 0.2em; }
    .sub-title { text-align: justify; font-size: 1.1rem; color: #333; margin-bottom: 1rem; padding: 0 4rem; }
    .quote { text-align: center; font-style: italic; color: #555; font-size: 1rem; margin-bottom: 2rem; }
    hr { border: none; height: 2px; background-color: #C8A200; margin-top: 10px; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# ========== Header Logo & Title ========== 
header1, header2 = st.columns([1, 16])
with header1:
    if os.path.exists("logo_babul.png"):
        st.image("logo_babul.png", width=60)
with header2:
    st.markdown(""" 
    <div style='display: flex; align-items: center; height: 100%;'>
        <h1 style='color:#A62639; font-size: 28px; margin: 0;'>BABUL KA'BAH</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ========== Sidebar Menu ========== 
st.sidebar.markdown("<h2 style='font-weight: bold;'>MENU</h2>", unsafe_allow_html=True)
sidebar_option = st.sidebar.radio("Pilih Menu", ("Input Data Calon Jemaah Umrah", "Visualisasi Histori"))

# ========== Form Input ========== 
if sidebar_option == "Input Data Calon Jemaah Umrah":
    st.markdown("<h2 class='main-title'>REKOMENDASI PAKET UMRAH</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Sistem ini dirancang untuk membantu memilih paket terbaik berdasarkan preferensi dan profil jamaah.</p>", unsafe_allow_html=True)
    st.markdown(""" 
    <p class='quote'>
        "Dan sempurnakanlah ibadah haji dan umrah karena Allah."<br>
        – <em>QS. Al-Baqarah: 196</em>
    </p>
    """, unsafe_allow_html=True)

    with st.form("form_umrah"):
        form_col1, form_col2 = st.columns(2)
        with form_col1:
            jenis_kelamin = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
            usia = st.number_input("Usia", min_value=18, max_value=100, value=30)
            wilayah_options = [
                "Jawa", "Sumatera", "Sulawesi", "Kalimantan", "Maluku", "Bali & Nusa Tenggara", "Papua"
            ]
            wilayah_geografis = st.selectbox("Wilayah Geografis", wilayah_options)

        with form_col2:
            tahun = st.selectbox("Tahun Keberangkatan", [2022, 2023])
            bulan_nama = [
                "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ]
            bulan_str = st.selectbox("Bulan Keberangkatan", bulan_nama)
            bulan_angka = bulan_nama.index(bulan_str) + 1
            bulan = bulan_angka if tahun == 2023 or (tahun == 2022 and bulan_angka == 12) else 0
            tanggal = st.number_input("Tanggal Keberangkatan", min_value=1, max_value=31, value=15)

        submit = st.form_submit_button("🔎 Lihat Rekomendasi")

    if submit:
        jk_encoded = 0 if jenis_kelamin.lower() == "pria" else 1
        wilayah_mapping = {name: i for i, name in enumerate(wilayah_options)}
        wilayah_encoded = wilayah_mapping.get(wilayah_geografis, 0)

        input_data = pd.DataFrame([{
            'jenis_kelamin': jk_encoded,
            'usia': usia,
            'wilayah_geografis': wilayah_encoded,
            'tanggal': tanggal,
            'bulan': bulan,
            'tahun': tahun
        }])

        try:
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
            }).sort_values(by='Probabilitas', ascending=False)
            prob_df['Harga'] = prob_df['Paket'].map(harga_paket)

            # Layout side by side
            col1, col2 = st.columns([1, 1.2], gap="large")

            with col1:
                st.markdown("### 📊 Rincian Probabilitas:")
                st.dataframe(
                    prob_df.set_index('Paket')[['Harga', 'Probabilitas']].style.format({
                        "Probabilitas": "{:.2%}"
                    }),
                    use_container_width=True
                )

            with col2:
                st.markdown("### 📈 Visualisasi Probabilitas:")
                fig, ax = plt.subplots(figsize=(8.5, 4.5))
                bars = ax.bar(prob_df['Paket'], prob_df['Probabilitas'], color='#4F7942')
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.1%}', xy=(bar.get_x() + bar.get_width()/2, height),
                                xytext=(0, 8), textcoords='offset points',
                                ha='center', va='bottom', fontsize=10)
                ax.set_title("Visualisasi Probabilitas Paket Umrah")
                ax.set_ylabel("Probabilitas")
                ax.set_xlabel("Nama Paket")
                ax.tick_params(axis='x', labelrotation=20)
                ax.grid(axis='y', linestyle='--', alpha=0.6)
                ax.set_axisbelow(True)
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses prediksi: {e}")

elif sidebar_option == "Visualisasi Histori":
    st.info("Bagian visualisasi histori belum diaktifkan. Tambahkan sesuai kebutuhan.")
