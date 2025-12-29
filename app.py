import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
# Gunakan URL LENGKAP agar koneksi lebih stabil
SPREADSHEET_URL = "docs.google.com"
ADMIN_PASSWORD = "ninja_rahasia"

st.set_page_config(page_title="Ninja Guild 2025 Permanent DB", page_icon="🥷", layout="wide")

# ==========================================
# 2. KONEKSI GOOGLE SHEETS
# ==========================================
# Inisialisasi koneksi menggunakan secrets format TOML yang ada di Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

# Fungsi untuk membaca data dengan cache 10 menit
@st.cache_data(ttl=600)
def load_data():
    try:
        # Membaca Sheet1 (pastikan nama tab di Google Sheets adalah Sheet1)
        df_data = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1")
        return df_data.fillna(0)
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame(columns=["Nama", "Advent", "Castle Rush"])

# Load data awal
df = load_data()

# ==========================================
# 3. ANTARMUKA PENGGUNA (UI)
# ==========================================
st.title("🏯 Markas Besar Ninja Guild (DB Permanen)")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📜 Struktur", "👥 Roster", "🌋 Advent", "🏰 Castle Rush", "⚙️ Admin Panel"
])

# --- TAB 2: ROSTER (Contoh Tampilan) ---
with tab2:
    st.subheader("👥 Daftar Anggota Aktif")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Data kosong atau belum terhubung.")

# --- TAB 5: ADMIN PANEL (Update Data) ---
with tab5:
    pwd = st.text_input("Password Admin", type="password")
    
    if pwd == ADMIN_PASSWORD:
        st.subheader("📝 Input Data Permanen")
        
        # Pilih Anggota dari kolom 'Nama'
        if 'Nama' in df.columns:
            target = st.selectbox("Pilih Anggota", df['Nama'].tolist())
            mode = st.radio("Pilih Konten yang Diupdate", ["Advent", "Castle Rush"])
            
            # Mendapatkan index baris anggota yang dipilih
            idx = df[df['Nama'] == target].index[0]
            
            # Input nilai baru berdasarkan mode yang dipilih
            if mode == "Advent":
                current_val = float(df.at[idx, 'Advent'])
                new_val = st.number_input(f"Skor Advent Baru untuk {target}", value=current_val)
                col = 'Advent'
            else:
                current_val = float(df.at[idx, 'Castle Rush'])
                new_val = st.number_input(f"Skor CR Baru untuk {target}", value=current_val)
                col = 'Castle Rush'

            if st.button(f"Simpan Perubahan {mode}"):
                # 1. Update dataframe lokal
                df.at[idx, col] = new_val
                
                # 2. Update ke Google Sheets secara permanen
                try:
                    conn.update(spreadsheet=SPREADSHEET_URL, data=df, worksheet="Sheet1")
                    st.success(f"Berhasil! Data {target} diperbarui di Google Sheets.")
                    
                    # 3. Bersihkan cache agar data terbaru langsung muncul
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan ke Google Sheets: {e}")
        else:
            st.error("Kolom 'Nama' tidak ditemukan di Google Sheets.")
    elif pwd != "":
        st.error("Password salah!")
    else:
        st.info("Masukkan password untuk mengakses fitur edit.")
