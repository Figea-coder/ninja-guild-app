import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# KONFIGURASI & KONSTANTA
# ==========================================
st.set_page_config(page_title="Ninja Guild 2025 DB", page_icon="🥷", layout="wide")

SHEET_URL = "1vOPqLuwRxvj4Of-t7owwmGvdGE06UjTl9Kve01vpZv0"
ADMIN_PASSWORD = "ninja_rahasia"
DAYS_OF_WEEK = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
ADVENT_HEROES = ["Teo", "Kyle", "Yeonhee", "Karma"]

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# LOGIKA DATA (BACKEND)
# ==========================================
class DatabaseManager:
    def __init__(self):
        self.conn = st.connection("gsheets", type=GSheetsConnection)

    @st.cache_data(ttl=60)
    def load_data(_self):
        """Memuat data dari Google Sheets dengan pembersihan dasar."""
        try:
            df = _self.conn.read(spreadsheet=SHEET_URL, worksheet="DataMember")
            if df.empty:
                return pd.DataFrame()
            
            # Pembersihan: Hapus baris tanpa nama dan isi NaN dengan 0
            df = df.dropna(subset=['Nama']).fillna(0)
            
            # Pastikan kolom numerik bertipe int/float
            numeric_cols = ADVENT_HEROES + DAYS_OF_WEEK + ['Total_Advent', 'Total_CR']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            st.error("Gagal terhubung ke database. Periksa koneksi atau izin Spreadsheet.")
            return pd.DataFrame()

    def update_data(self, updated_df):
        """Menulis data kembali ke Google Sheets."""
        try:
            self.conn.update(spreadsheet=SHEET_URL, worksheet="DataMember", data=updated_df)
            st.cache_data.clear()
            st.success("✅ Database Berhasil Diperbarui!")
            st.rerun()
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            st.error(f"Gagal menyimpan data: {e}")

db = DatabaseManager()
df = db.load_data()

# ==========================================
# ANTARMUKA PENGGUNA (UI)
# ==========================================
st.title("🏯 Markas Besar Ninja Guild")
st.caption(f"📅 Update Terakhir: {datetime.now().strftime('%d %B %Y %H:%M')}")

if df.empty:
    st.warning("⚠️ Data tidak ditemukan atau gagal dimuat.")
    st.stop()

tabs = st.tabs(["📜 Struktur", "👥 Roster", "🌋 Advent", "🏰 Castle Rush", "⚙️ Admin"])

# --- TAB ROSTER ---
with tabs[1]:
    st.subheader("Daftar Anggota")
    st.dataframe(
        df[['Nama', 'Total_Advent', 'Total_CR']], 
        use_container_width=True, 
        hide_index=True
    )

# --- TAB ADMIN ---
with tabs[4]:
    with st.form("admin_login"):
        pwd = st.text_input("Password Admin", type="password")
        login_btn = st.form_submit_button("Masuk")

    if pwd == ADMIN_PASSWORD:
        st.info("🔓 Mode Admin Aktif")
        
        target_ninja = st.selectbox("Pilih Ninja", df['Nama'].tolist())
        idx = df[df['Nama'] == target_ninja].index[0]
        
        mode = st.radio("Kategori Update", ["Advent", "Castle Rush"], horizontal=True)
        
        with st.container(border=True):
            if mode == "Advent":
                cols = st.columns(4)
                new_vals = {}
                for i, hero in enumerate(ADVENT_HEROES):
                    with cols[i]:
                        new_vals[hero] = st.number_input(hero, value=int(df.at[idx, hero]))
                
                if st.button("💾 Simpan Data Advent"):
                    for hero, val in new_vals.items():
                        df.at[idx, hero] = val
                    df.at[idx, 'Total_Advent'] = sum(new_vals.values())
                    db.update_data(df)

            else: # Castle Rush
                col_a, col_b = st.columns(2)
                with col_a:
                    hari = st.selectbox("Pilih Hari", DAYS_OF_WEEK)
                with col_b:
                    skor = st.number_input(f"Skor {hari}", value=int(df.at[idx, hari]))
                
                if st.button(f"💾 Simpan Skor {hari}"):
                    df.at[idx, hari] = skor
                    df.at[idx, 'Total_CR'] = df.loc[idx, DAYS_OF_WEEK].sum()
                    db.update_data(df)
    elif pwd:
        st.error("❌ Password Salah!")

# --- DEBUG INFO ---
with st.expander("🔍 System Info"):
    st.write(f"Baris Data: {len(df)}")
    if st.button("Force Clear Cache"):
        st.cache_data.clear()
        st.rerun()
