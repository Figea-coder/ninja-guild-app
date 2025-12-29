import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
# Link Google Sheets kamu. ID diambil dari URL.
SPREADSHEET_ID = "docs.google.com"
ADMIN_PASSWORD = "ninja_rahasia"

st.set_page_config(page_title="Ninja Guild 2025 Permanent DB", page_icon="🥷", layout="wide")

# ==========================================
# 2. KONEKSI GOOGLE SHEETS (MODE MENULIS/EDIT)
# ==========================================
# Koneksi ini akan otomatis mencari secrets di Streamlit Cloud untuk otentikasi
conn = st.connection("gsheets", type=GSheetsConnection)

# Fungsi untuk membaca dan menulis data
def load_data():
    # Baca data dari Sheet1
    df_data = conn.read(spreadsheet=SPREADSHEET_ID, worksheet="Sheet1", usecols=list(range(15)), ttl="10m")
    return df_data.fillna(0)

# ==========================================
# 3. LOGIKA APLIKASI
# ==========================================
# Load data saat aplikasi berjalan
df = load_data()
hari_ini = datetime.now().strftime('%A')
is_admin = False # Default, login via panel

st.title("🏯 Markas Besar Ninja Guild (DB Permanen)")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📜 Struktur", "👥 Roster", "🌋 Advent", "🏰 Castle Rush", "⚙️ Admin Panel"
])

# --- TAB 1: STRUKTUR ---
with tab1:
    # ... (Isi tampilan struktur sama seperti sebelumnya) ...
    st.success("Tampilan struktur & roster ada di sini.")

# --- TAB 2: ROSTER ---
with tab2:
    st.subheader("👥 Daftar Anggota Aktif")
    st.table(df[['Nama']])

# --- TAB 5: ADMIN PANEL (Input & Write Back) ---
with tab5:
    pwd = st.text_input("Password Admin", type="password")
    if pwd == ADMIN_PASSWORD:
        is_admin = True
        st.subheader("📝 Input Data Permanen")
        
        target = st.selectbox("Pilih Anggota", df['Nama'].tolist())
        mode = st.radio("Pilih Konten", ["Advent", "Castle Rush"])
        
        # Mencari index baris ninja yang dipilih
        idx = df[df['Nama'] == target].index[0]

        if mode == "Advent":
            # Ambil nilai saat ini dari kolom 'Advent'
            nilai_sekarang = float(df.at[idx, 'Advent'])
            skor_baru = st.number_input("Masukkan Skor Advent Baru", value=nilai_sekarang)
            
            if st.button("Simpan Permanen Advent"):
                # UPDATE DATAFRAME LOKAL DULU
                df.at[idx, 'Advent'] = skor_baru
                # KIRIM KE GOOGLE SHEETS
                conn.update(spreadsheet=SPREADSHEET_ID, data=df, worksheet="Sheet1")
                st.success(f"Skor Advent {target} berhasil diupdate!"); st.rerun()
        
        elif mode == "Castle Rush":
            # Ambil nilai saat ini dari kolom 'Castle Rush'
            nilai_sekarang_cr = float(df.at[idx, 'Castle Rush'])
            skor_cr_baru = st.number_input("Masukkan Skor CR Baru", value=nilai_sekarang_cr)
            
            if st.button("Simpan Permanen CR"):
                # UPDATE DATAFRAME LOKAL DULU
                df.at[idx, 'Castle Rush'] = skor_cr_baru
                # KIRIM KE GOOGLE SHEETS
                conn.update(spreadsheet=SPREADSHEET_ID, data=df, worksheet="Sheet1")
                st.success(f"Skor CR {target} berhasil diupdate!"); st.rerun()
    else:
        st.warning("Silakan login untuk mengedit data.")
