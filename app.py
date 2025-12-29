import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import gspread # Library tambahan untuk koneksi yang lebih kuat

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
SPREADSHEET_ID_RAW = "1vOPqLuwRxvj4Of-t7owwmGvdGE06UjTl9Kve01vpZv0"
SPREADSHEET_URL_EDIT = f"docs.google.com{SPREADSHEET_ID_RAW}/edit"
ADMIN_PASSWORD = "ninja_rahasia"

st.set_page_config(page_title="Ninja Guild 2025 DB", page_icon="🥷", layout="wide")

# ==========================================
# 2. FUNGSI BACA DATA (Baca via Link Publik)
# ==========================================
@st.cache_data(ttl=60) # Cache singkat agar update cepat terlihat
def load_data():
    try:
        # Menggunakan link CSV download publik untuk MEMBACA data (solusi Error 400/404)
        csv_url = f"docs.google.com{SPREADSHEET_ID_RAW}/export?format=csv&gid=0"
        df_clean = pd.read_csv(csv_url).dropna(subset=['Nama']).fillna(0)
        return df_clean
    except Exception as e:
        st.error(f"Gagal memuat data: {e}. Pastikan Google Sheets di-Share ke 'Anyone with the link'.")
        return pd.DataFrame()

df = load_data()

# ==========================================
# 3. FUNGSI MENULIS DATA (Via Otentikasi Service Account)
# ==========================================
def write_to_gsheets(dataframe):
    try:
        # Menggunakan koneksi st-gsheets-connection untuk MENULIS (butuh Secrets TOML)
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(spreadsheet=SPREADSHEET_URL_EDIT, data=dataframe, worksheet="Sheet1")
        st.success("Database diperbarui secara permanen!")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Gagal menyimpan ke Google Sheets: {e}")

# ==========================================
# 4. ANTARMUKA (UI) & LOGIC
# ==========================================
st.title("🏯 Markas Besar Ninja Guild")
st.markdown(f"**Update Terakhir:** {datetime.now().strftime('%d %B %Y %H:%M')}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📜 Struktur", "👥 Roster", "🌋 Advent", "🏰 Castle Rush", "⚙️ Admin Panel"
])

# --- TAB 2: ROSTER ---
with tab2:
    st.subheader("👥 Daftar Anggota & Status Total")
    if not df.empty:
        st.dataframe(df[['Nama', 'Total_Advent', 'Total_CR']], use_container_width=True)

# --- TAB 3: ADVENT ---
with tab3:
    st.subheader("🌋 Detail Skor Advent")
    kolom_advent = ['Nama', 'Teo', 'Kyle', 'Yeonhee', 'Karma', 'Total_Advent', 'Tiket_Terpakai']
    if not df.empty and all(col in df.columns for col in kolom_advent):
        st.table(df[kolom_advent])

# --- TAB 4: CASTLE RUSH ---
with tab4:
    st.subheader("🏰 Detail Skor Castle Rush")
    kolom_cr = ['Nama', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu', 'Total_CR']
    if not df.empty and all(col in df.columns for col in kolom_cr):
        st.table(df[kolom_cr])

# --- TAB 5: ADMIN PANEL ---
with tab5:
    pwd = st.text_input("Password Admin", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("Mode Admin Aktif")
        
        if 'Nama' in df.columns and not df.empty:
            target = st.selectbox("Pilih Ninja", df['Nama'].tolist())
            mode = st.radio("Kategori Update", ["Advent", "Castle Rush"])
            
            idx_pos = df[df['Nama'] == target].index

            if mode == "Advent":
                col1, col2, col3, col4 = st.columns(4)
                with col1: t_teo = st.number_input("Teo", value=int(df.at[idx_pos, 'Teo']))
                with col2: t_kyle = st.number_input("Kyle", value=int(df.at[idx_pos, 'Kyle']))
                with col3: t_yeon = st.number_input("Yeonhee", value=int(df.at[idx_pos, 'Yeonhee']))
                with col4: t_karma = st.number_input("Karma", value=int(df.at[idx_pos, 'Karma']))
                tiket = st.number_input("Tiket Terpakai", value=int(df.at[idx_pos, 'Tiket_Terpakai']))
                
                if st.button("💾 Simpan Data Advent"):
                    df.at[idx_pos, 'Teo'] = t_teo
                    df.at[idx_pos, 'Kyle'] = t_kyle
                    df.at[idx_pos, 'Yeonhee'] = t_yeon
                    df.at[idx_pos, 'Karma'] = t_karma
                    df.at[idx_pos, 'Tiket_Terpakai'] = tiket
                    df.at[idx_pos, 'Total_Advent'] = t_teo + t_kyle + t_yeon + t_karma
                    write_to_gsheets(df) # Panggil fungsi tulis

            elif mode == "Castle Rush":
                hari = st.selectbox("Pilih Hari", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"])
                skor_hari = st.number_input(f"Skor {hari}", value=int(df.at[idx_pos, hari]))
                
                if st.button(f"💾 Simpan Skor {hari}"):
                    df.at[idx_pos, hari] = skor_hari
                    df.at[idx_pos, 'Total_CR'] = df.loc[idx_pos, ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']].sum(axis=1)
                    write_to_gsheets(df) # Panggil fungsi tulis
        else:
            st.error("Kolom 'Nama' tidak ditemukan atau data kosong.")
    elif pwd != "":
        st.info("Silakan login.")

