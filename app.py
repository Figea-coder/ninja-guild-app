import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
# Link Google Sheets kamu. ID diambil dari URL.
SPREADSHEET_ID = "1vOPqLuwRxvj4Of-t7owwmGvdGE06UjTl9Kve01vpZv0"
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
        idx = df[df['Nama'] == target].index[0]

        if mode == "Advent":
            # ... (Tampilan input Advent sama seperti sebelumnya) ...
            if st.button("Simpan Permanen Advent"):
                # LOGIKA MENULIS KEMBALI KE GOOGLE SHEETS
                conn.update(spreadsheet=SPREADSHEET_ID, data=df, worksheet="Sheet1")
                st.success("Data Advent tersimpan permanen!"); st.rerun()
        
        elif mode == "Castle Rush":
             # ... (Tampilan input CR sama seperti sebelumnya) ...
            if st.button("Simpan Permanen CR"):
                 # LOGIKA MENULIS KEMBALI KE GOOGLE SHEETS
                conn.update(spreadsheet=SPREADSHEET_ID, data=df, worksheet="Sheet1")
                st.success("Skor CR tersimpan permanen!"); st.rerun()
    else:
        st.warning("Silakan login untuk mengedit data.")
