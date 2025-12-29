import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
# URL HARUS LENGKAP DENGAN https://
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1vOPqLuwRxvj4Of-t7owwmGvdGE06UjTl9Kve01vpZv0/edit"
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
            
            # Mengambil index (kita tahu ini cuma 1 baris)
            idx_pos = df[df['Nama'] == target].index[0]

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
                    
                    conn.update(spreadsheet=SPREADSHEET_URL, data=df, worksheet="Sheet1")
                    st.success("Database diperbarui!"); st.cache_data.clear(); st.rerun()

            elif mode == "Castle Rush":
                hari = st.selectbox("Pilih Hari", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"])
                skor_hari = st.number_input(f"Skor {hari}", value=int(df.at[idx_pos, hari]))
                
                if st.button(f"💾 Simpan Skor {hari}"):
                    df.at[idx_pos, hari] = skor_hari
                    # Hitung otomatis Total CR dari semua kolom hari
                    df.at[idx_pos, 'Total_CR'] = df.loc[idx_pos, ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']].sum()
                    
                    conn.update(spreadsheet=SPREADSHEET_URL, data=df, worksheet="Sheet1")
                    st.success(f"Skor {hari} tersimpan!"); st.cache_data.clear(); st.rerun()
        else:
            st.error("Kolom 'Nama' tidak ditemukan atau data kosong.")
    elif pwd != "":
        st.info("Masukkan password admin.")
