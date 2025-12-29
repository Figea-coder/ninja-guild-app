import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
SPREADSHEET_URL = "docs.google.com"
ADMIN_PASSWORD = "ninja_rahasia"

st.set_page_config(page_title="Ninja Guild 2025 Permanent DB", page_icon="🥷", layout="wide")

# ==========================================
# 2. KONEKSI & LOAD DATA
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=600)
def load_data():
    try:
        # Membaca Sheet1
        df_data = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1")
        return df_data.fillna(0)
    except Exception as e:
        st.error(f"Gagal memuat data: {e}. Pastikan Google Sheets sudah di-share ke email robot.")
        return pd.DataFrame(columns=["Nama", "Advent", "Castle Rush"])

df = load_data()

# ==========================================
# 3. TAMPILAN UTAMA (UI)
# ==========================================
st.title("🏯 Markas Besar Ninja Guild (2025)")
st.markdown(f"**Hari Ini:** {datetime.now().strftime('%A, %d %B %Y')}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📜 Struktur", "👥 Roster", "🌋 Advent", "🏰 Castle Rush", "⚙️ Admin Panel"
])

# --- TAB 1: STRUKTUR ---
with tab1:
    st.subheader("📜 Struktur Organisasi")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Guild Master:** [Nama GM]")
        st.success("**Vice Master:** [Nama Vice]")
    with col2:
        st.warning("**Target Guild:** Top 100")

# --- TAB 2: ROSTER ---
with tab2:
    st.subheader("👥 Daftar Anggota Aktif")
    if not df.empty:
        st.dataframe(df[['Nama']], use_container_width=True)

# --- TAB 3: ADVENT ---
with tab3:
    st.subheader("🌋 Skor Advent Season Ini")
    if 'Advent' in df.columns:
        st.bar_chart(df.set_index('Nama')['Advent'])
        st.table(df[['Nama', 'Advent']].sort_values(by='Advent', ascending=False))

# --- TAB 4: CASTLE RUSH ---
with tab4:
    st.subheader("🏰 Skor Castle Rush")
    if 'Castle Rush' in df.columns:
        st.table(df[['Nama', 'Castle Rush']].sort_values(by='Castle Rush', ascending=False))

# --- TAB 5: ADMIN PANEL (Input Data Permanen) ---
with tab5:
    pwd = st.text_input("Password Admin", type="password")
    
    if pwd == ADMIN_PASSWORD:
        st.success("Akses Diterima. Silakan Update Data.")
        
        if 'Nama' in df.columns:
            target = st.selectbox("Pilih Nama Ninja", df['Nama'].tolist())
            mode = st.radio("Update Skor Untuk:", ["Advent", "Castle Rush"])
            
            idx = df[df['Nama'] == target].index
            
            if mode == "Advent":
                current_val = float(df.at[idx[0], 'Advent'])
                new_val = st.number_input(f"Input Skor Advent Baru ({target})", value=current_val)
                col_name = 'Advent'
            else:
                current_val = float(df.at[idx[0], 'Castle Rush'])
                new_val = st.number_input(f"Input Skor CR Baru ({target})", value=current_val)
                col_name = 'Castle Rush'

            if st.button("💾 Simpan Permanen ke Google Sheets"):
                # Update DataFrame
                df.at[idx, col_name] = new_val
                try:
                    # Tulis balik ke Google Sheets
                    conn.update(spreadsheet=SPREADSHEET_URL, data=df, worksheet="Sheet1")
                    st.balloons()
                    st.success(f"Data {target} Berhasil Diperbarui!")
                    st.cache_data.clear() # Paksa aplikasi ambil data baru
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal Simpan: {e}")
    elif pwd != "":
        st.error("Password Salah!")
