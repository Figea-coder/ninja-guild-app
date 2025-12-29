import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
# GANTI LINK DI BAWAH INI DENGAN LINK GOOGLE SHEETS KAMU
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vOPqLuwRxvj4Of-t7owwmGvdGE06UjTl9Kve01vpZv0/edit?gid=0#gid=0"
ADMIN_PASSWORD = "ninja_rahasia"

st.set_page_config(page_title="Ninja Guild 2025", page_icon="🥷", layout="wide")

# Fungsi untuk membaca data dari Google Sheets (CSV Export Link)
def load_data():
    try:
        # Mengubah link share menjadi link export CSV
        csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')
        csv_url = csv_url.replace('/edit#gid=0', '/export?format=csv')
        return pd.read_csv(csv_url).fillna(0)
    except:
        # Jika gagal (link salah), gunakan data internal sementara
        return pd.DataFrame(columns=["Nama", "Teo", "Kyle", "Yeonhee", "Karma", "Total_Advent", "Tiket_Terpakai", "Total_CR"])

# Load data di awal
if 'df' not in st.session_state:
    st.session_state['df'] = load_data()

df = st.session_state['df']
hari_ini = datetime.now().strftime('%A')

# ==========================================
# 2. SIDEBAR ADMIN
# ==========================================
with st.sidebar:
    st.header("🔑 Admin Login")
    pwd = st.text_input("Password", type="password")
    is_admin = (pwd == ADMIN_PASSWORD)
    
    st.markdown("---")
    st.write(f"📅 **Hari Ini:** {hari_ini}")
    st.link_button("📂 Buka Google Sheets", SHEET_URL)
    st.caption("Gunakan tombol di atas untuk edit manual jika ada kesalahan.")

# ==========================================
# 3. TAMPILAN UTAMA
# ==========================================
st.title("🏯 Markas Besar Ninja Guild")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📜 Struktur", "👥 Roster", "🌋 Advent (13 Tiket)", "🏰 Castle Rush", "⚙️ Admin Panel"
])

# --- TAB 1: STRUKTUR ---
with tab1:
    st.subheader("📌 Struktur Organisasi & Frontliners")
    c1, c2 = st.columns(2)
    with c1:
        st.info("👑 **Guild Master**\n\n- DimasBT")
        st.warning("⚔️ **Vice Master**\n\n- DakDecull")
    with c2:
        st.success("🛡️ **Frontliners (Top 5 CR)**")
        if 'Total_CR' in df.columns:
            top5 = df.sort_values(by="Total_CR", ascending=False).head(5)['Nama'].tolist()
            for i, p in enumerate(top5, 1): st.write(f"{i}. {p}")

# --- TAB 2: ROSTER ---
with tab2:
    st.subheader("👥 Daftar Anggota Aktif")
    st.table(df[['Nama']])

# --- TAB 3: ADVENT ---
with tab3:
    st.subheader("🌋 Leaderboard Advent")
    if 'Total_Advent' in df.columns:
        view_adv = df[['Nama', 'Teo', 'Kyle', 'Yeonhee', 'Karma', 'Total_Advent', 'Tiket_Terpakai']]
        st.dataframe(view_adv.sort_values(by="Total_Advent", ascending=False), use_container_width=True)

# --- TAB 4: CASTLE RUSH ---
with tab4:
    st.subheader("🏰 Leaderboard Castle Rush")
    cols_cr = ['Nama', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu', 'Total_CR']
    if all(c in df.columns for c in cols_cr):
        st.dataframe(df[cols_cr].sort_values(by="Total_CR", ascending=False), use_container_width=True)

# --- TAB 5: ADMIN PANEL ---
with tab5:
    if is_admin:
        st.subheader("📝 Update Skor Member")
        target = st.selectbox("Pilih Anggota", df['Nama'].tolist())
        mode = st.radio("Pilih Konten", ["Advent", "Castle Rush"])
        
        idx = df[df['Nama'] == target].index[0]
        
        if mode == "Advent":
            cur_tkt = df.at[idx, 'Tiket_Terpakai']
            st.write(f"Tiket {target}: **{int(cur_tkt)}/13**")
            c1, c2 = st.columns(2)
            t = c1.number_input("Teo", value=int(df.at[idx, 'Teo']))
            k = c1.number_input("Kyle", value=int(df.at[idx, 'Kyle']))
            y = c2.number_input("Yeonhee", value=int(df.at[idx, 'Yeonhee']))
            kr = c2.number_input("Karma", value=int(df.at[idx, 'Karma']))
            
            if st.button("Simpan Advent"):
                df.at[idx, 'Teo'] = t
                df.at[idx, 'Kyle'] = k
                df.at[idx, 'Yeonhee'] = y
                df.at[idx, 'Karma'] = kr
                df.at[idx, 'Total_Advent'] = t+k+y+kr
                df.at[idx, 'Tiket_Terpakai'] = cur_tkt + 1
                st.session_state['df'] = df
                st.success("Data diperbarui di web! Silakan salin ke G-Sheet jika perlu.")
        
        else:
            hari_pilih = st.selectbox("Pilih Hari", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"])
            skor_cr = st.number_input(f"Skor {hari_pilih}", value=int(df.at[idx, hari_pilih]))
            if st.button("Simpan CR"):
                df.at[idx, hari_pilih] = skor_cr
                # Hitung ulang total CR
                days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                df.at[idx, 'Total_CR'] = df.loc[idx, days].sum()
                st.session_state['df'] = df
                st.success("Skor CR diperbarui!")
                
        st.divider()
        st.warning("Catatan: Karena keterbatasan API di PyCafe Free, data yang kamu input di sini harus kamu 'Copy-Paste' manual ke Google Sheets jika ingin permanen selamanya.")
    else:
        st.warning("Silakan login untuk mengedit data.")
