import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
SPREADSHEET_URL = "docs.google.com"
ADMIN_PASSWORD = "ninja_rahasia"

st.set_page_config(page_title="Ninja Guild 2025 DB", page_icon="🥷", layout="wide")

# ==========================================
# 2. KONEKSI & LOAD DATA
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60) # Cache singkat agar update cepat terlihat
def load_data():
    try:
        # Membaca data dan membersihkan baris kosong
        df_raw = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1")
        df_clean = df_raw.dropna(subset=['Nama']) # Hapus baris yang Namanya kosong
        return df_clean.fillna(0)
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

df = load_data()

# ==========================================
# 3. ANTARMUKA (UI)
# ==========================================
st.title("🏯 Markas Besar Ninja Guild")
st.markdown(f"**Update Terakhir:** {datetime.now().strftime('%d %B %Y %H:%M')}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📜 Struktur", "👥 Roster", "🌋 Advent", "🏰 Castle Rush", "⚙️ Admin Panel"
])

# --- TAB 2: ROSTER ---
with tab2:
    st.subheader("👥 Daftar Anggota & Status Total")
    # Menampilkan Nama, Total Advent, dan Total CR saja agar rapi
    if not df.empty:
        st.dataframe(df[['Nama', 'Total_Advent', 'Total_CR']], use_container_width=True)

# --- TAB 3: ADVENT ---
with tab3:
    st.subheader("🌋 Detail Skor Advent")
    # Menampilkan kolom Advent saja
    kolom_advent = ['Nama', 'Teo', 'Kyle', 'Yeonhee', 'Karma', 'Total_Advent', 'Tiket_Terpakai']
    st.table(df[kolom_advent])

# --- TAB 4: CASTLE RUSH ---
with tab4:
    st.subheader("🏰 Detail Skor Castle Rush")
    # Menampilkan kolom CR (Senin-Minggu)
    kolom_cr = ['Nama', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu', 'Total_CR']
    st.table(df[kolom_cr])

# --- TAB 5: ADMIN PANEL ---
with tab5:
    pwd = st.text_input("Password Admin", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("Mode Admin Aktif")
        
        target = st.selectbox("Pilih Ninja", df['Nama'].tolist())
        mode = st.radio("Kategori Update", ["Advent", "Castle Rush"])
        idx = df[df['Nama'] == target].index

        if mode == "Advent":
            col1, col2, col3, col4 = st.columns(4)
            with col1: t_teo = st.number_input("Teo", value=int(df.at[idx[0], 'Teo']))
            with col2: t_kyle = st.number_input("Kyle", value=int(df.at[idx[0], 'Kyle']))
            with col3: t_yeon = st.number_input("Yeonhee", value=int(df.at[idx[0], 'Yeonhee']))
            with col4: t_karma = st.number_input("Karma", value=int(df.at[idx[0], 'Karma']))
            tiket = st.number_input("Tiket Terpakai", value=int(df.at[idx[0], 'Tiket_Terpakai']))
            
            if st.button("💾 Simpan Data Advent"):
                df.at[idx, 'Teo'] = t_teo
                df.at[idx, 'Kyle'] = t_kyle
                df.at[idx, 'Yeonhee'] = t_yeon
                df.at[idx, 'Karma'] = t_karma
                df.at[idx, 'Tiket_Terpakai'] = tiket
                # Hitung otomatis total
                df.at[idx, 'Total_Advent'] = t_teo + t_kyle + t_yeon + t_karma
                
                conn.update(spreadsheet=SPREADSHEET_URL, data=df, worksheet="Sheet1")
                st.success("Database diperbarui!"); st.cache_data.clear(); st.rerun()

        elif mode == "Castle Rush":
            hari = st.selectbox("Pilih Hari", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"])
            skor_hari = st.number_input(f"Skor {hari}", value=int(df.at[idx[0], hari]))
            
            if st.button(f"💾 Simpan Skor {hari}"):
                df.at[idx, hari] = skor_hari
                # Hitung otomatis Total CR dari semua kolom hari
                df.at[idx, 'Total_CR'] = df.loc[idx, ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']].sum(axis=1)
                
                conn.update(spreadsheet=SPREADSHEET_URL, data=df, worksheet="Sheet1")
                st.success(f"Skor {hari} tersimpan!"); st.cache_data.clear(); st.rerun()
    else:
        st.info("Silakan login.")
