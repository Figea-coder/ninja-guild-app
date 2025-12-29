import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 0. KONFIGURASI LOGGING (Untuk Debug)
# ==========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
st.set_page_config(page_title="Ninja Guild 2025 DB", page_icon="🥷", layout="wide")

# Verifikasi ID Spreadsheet (Pastikan ini benar)
SPREADSHEET_ID = "1vOPqLuwRxvj4Of-t7owwmGvdGE06UjTl9Kve01vpZv0"
SPREADSHEET_URL = f"docs.google.com{SPREADSHEET_ID}/edit#gid=0"
ADMIN_PASSWORD = "ninja_rahasia"

# ==========================================
# 2. INISIALISASI KONEKSI
# ==========================================
try:
    logger.info("Mencoba menginisialisasi GSheetsConnection...")
    conn = st.connection("gsheets", type=GSheetsConnection)
    logger.info("Koneksi berhasil diinisialisasi.")
except Exception as e:
    logger.error(f"Gagal inisialisasi koneksi: {str(e)}")
    st.error(f"Koneksi GSheets Gagal: {e}")

# ==========================================
# 3. FUNGSI BACA DATA (DENGAN LOG)
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    start_time = datetime.now()
    logger.info(f"Mulai load_data() pada {start_time}")
    
    try:
        logger.info(f"Mencoba membaca URL: {SPREADSHEET_URL}")
        # Membaca data
        data = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1")
        
        if data is None or data.empty:
            logger.warning("Data berhasil dibaca tapi kosong!")
            return pd.DataFrame()
            
        # Pembersihan data
        df_clean = data.dropna(subset=['Nama']).fillna(0)
        
        logger.info(f"Berhasil memuat {len(df_clean)} baris data.")
        return df_clean

    except Exception as e:
        logger.error(f"Error pada load_data: {str(e)}")
        # Log detail khusus jika 404
        if "404" in str(e):
            st.error("Error 404: File tidak ditemukan atau Service Account tidak punya akses.")
        else:
            st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

df = load_data()

# ==========================================
# 4. FUNGSI MENULIS DATA (DENGAN LOG)
# ==========================================
def write_to_gsheets(updated_df):
    logger.info("Memulai proses penulisan ke Google Sheets...")
    try:
        conn.update(
            spreadsheet=SPREADSHEET_URL,
            worksheet="Sheet1",
            data=updated_df
        )
        logger.info("Update berhasil dikirim ke Google Sheets.")
        st.success("✅ Database Berhasil Diperbarui!")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        logger.error(f"Gagal menulis data: {str(e)}")
        st.error(f"Gagal menyimpan: {e}")

# ==========================================
# 5. ANTARMUKA (UI)
# ==========================================
st.title("🏯 Markas Besar Ninja Guild")
st.markdown(f"📅 **Update Terakhir:** {datetime.now().strftime('%d %B %Y %H:%M')}")

# Panel Debug (Opsional: Hanya tampil di log server/terminal)
with st.expander("🔍 Debug Info (Klik untuk detail)"):
    st.write(f"Spreadsheet ID: `{SPREADSHEET_ID}`")
    st.write(f"Baris Terdeteksi: {len(df) if not df.empty else 0}")
    if st.button("Hapus Cache & Reload"):
        st.cache_data.clear()
        st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📜 Struktur", "👥 Roster", "🌋 Advent", "🏰 Castle Rush", "⚙️ Admin Panel"
])

# --- TAB 2: ROSTER ---
with tab2:
    st.subheader("👥 Daftar Anggota")
    if not df.empty:
        st.dataframe(df[['Nama', 'Total_Advent', 'Total_CR']], use_container_width=True)
    else:
        st.warning("Data Roster Kosong.")

# --- TAB 5: ADMIN PANEL ---
with tab5:
    pwd = st.text_input("Password Admin", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("Mode Admin Aktif")
        
        if not df.empty:
            target = st.selectbox("Pilih Ninja", df['Nama'].tolist())
            mode = st.radio("Kategori Update", ["Advent", "Castle Rush"])
            idx = df[df['Nama'] == target].index

            if mode == "Advent":
                c1, c2, c3, c4 = st.columns(4)
                with c1: t_teo = st.number_input("Teo", value=int(df.at[idx[0], 'Teo']))
                with c2: t_kyle = st.number_input("Kyle", value=int(df.at[idx[0], 'Kyle']))
                with c3: t_yeon = st.number_input("Yeonhee", value=int(df.at[idx[0], 'Yeonhee']))
                with c4: t_karma = st.number_input("Karma", value=int(df.at[idx[0], 'Karma']))
                
                if st.button("💾 Simpan Data Advent"):
                    logger.info(f"Admin mencoba update data Advent untuk: {target}")
                    df.at[idx[0], 'Teo'] = t_teo
                    df.at[idx[0], 'Kyle'] = t_kyle
                    df.at[idx[0], 'Yeonhee'] = t_yeon
                    df.at[idx[0], 'Karma'] = t_karma
                    df.at[idx[0], 'Total_Advent'] = t_teo + t_kyle + t_yeon + t_karma
                    write_to_gsheets(df)

            elif mode == "Castle Rush":
                hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                hari = st.selectbox("Pilih Hari", hari_list)
                skor_hari = st.number_input(f"Skor {hari}", value=int(df.at[idx[0], hari]))
                
                if st.button(f"💾 Simpan Skor {hari}"):
                    logger.info(f"Admin mencoba update data CR {hari} untuk: {target}")
                    df.at[idx[0], hari] = skor_hari
                    df.at[idx[0], 'Total_CR'] = sum([df.at[idx[0], h] for h in hari_list])
                    write_to_gsheets(df)
    elif pwd != "":
        st.error("Password Salah!")
