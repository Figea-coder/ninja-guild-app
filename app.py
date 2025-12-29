import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. KONFIGURASI & KONEKSI
# ==========================================
st.set_page_config(page_title="Ninja Guild 2025 DB", page_icon="🥷", layout="wide")

# Masukkan ID Spreadsheet Anda
SPREADSHEET_ID = "1vOPqLuwRxvj4Of-t7owwmGvdGE06UjTl9Kve01vpZv0"
# URL Lengkap dengan Protokol HTTPS
SPREADSHEET_URL = f"docs.google.com{SPREADSHEET_ID}/edit#gid=0"
ADMIN_PASSWORD = "ninja_rahasia"

# Inisialisasi koneksi (Membaca dari .streamlit/secrets.toml)
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNGSI BACA DATA
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    try:
        # Menyertakan spreadsheet=SPREADSHEET_URL mengatasi error "Spreadsheet must be specified"
        data = conn.read(
            spreadsheet=SPREADSHEET_URL, 
            worksheet="Sheet1", 
            ttl="1m"
        )
        # Bersihkan data: Hapus baris kosong di kolom 'Nama', isi sel kosong dengan 0
        df_clean = data.dropna(subset=['Nama']).fillna(0)
        return df_clean
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

df = load_data()

# ==========================================
# 3. FUNGSI MENULIS DATA
# ==========================================
def write_to_gsheets(updated_df):
    try:
        # Update ke Google Sheets
        conn.update(
            spreadsheet=SPREADSHEET_URL,
            worksheet="Sheet1",
            data=updated_df
        )
        st.success("✅ Database Google Sheets Berhasil Diperbarui!")
        st.cache_data.clear() # Reset cache agar data baru langsung muncul
        st.rerun()
    except Exception as e:
        st.error(f"Gagal menyimpan ke Google Sheets: {e}")

# ==========================================
# 4. ANTARMUKA (UI)
# ==========================================
st.title("🏯 Markas Besar Ninja Guild")
st.markdown(f"📅 **Update Terakhir:** {datetime.now().strftime('%d %B %Y %H:%M')}")

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
    if not df.empty:
        st.table(df[kolom_advent])

# --- TAB 4: CASTLE RUSH ---
with tab4:
    st.subheader("🏰 Detail Skor Castle Rush")
    kolom_cr = ['Nama', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu', 'Total_CR']
    if not df.empty:
        st.table(df[kolom_cr])

# --- TAB 5: ADMIN PANEL ---
with tab5:
    pwd = st.text_input("Password Admin", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("Mode Admin Aktif")
        
        if not df.empty:
            target = st.selectbox("Pilih Ninja", df['Nama'].tolist())
            mode = st.radio("Kategori Update", ["Advent", "Castle Rush"])
            
            # Cari index dari ninja yang dipilih
            idx = df[df['Nama'] == target].index[0]

            if mode == "Advent":
                c1, c2, c3, c4 = st.columns(4)
                with c1: t_teo = st.number_input("Teo", value=int(df.at[idx, 'Teo']))
                with c2: t_kyle = st.number_input("Kyle", value=int(df.at[idx, 'Kyle']))
                with c3: t_yeon = st.number_input("Yeonhee", value=int(df.at[idx, 'Yeonhee']))
                with c4: t_karma = st.number_input("Karma", value=int(df.at[idx, 'Karma']))
                tiket = st.number_input("Tiket Terpakai", value=int(df.at[idx, 'Tiket_Terpakai']))
                
                if st.button("💾 Simpan Data Advent"):
                    df.at[idx, 'Teo'] = t_teo
                    df.at[idx, 'Kyle'] = t_kyle
                    df.at[idx, 'Yeonhee'] = t_yeon
                    df.at[idx, 'Karma'] = t_karma
                    df.at[idx, 'Tiket_Terpakai'] = tiket
                    df.at[idx, 'Total_Advent'] = t_teo + t_kyle + t_yeon + t_karma
                    write_to_gsheets(df)

            elif mode == "Castle Rush":
                hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                hari = st.selectbox("Pilih Hari", hari_list)
                skor_hari = st.number_input(f"Skor {hari}", value=int(df.at[idx, hari]))
                
                if st.button(f"💾 Simpan Skor {hari}"):
                    df.at[idx, hari] = skor_hari
                    # Hitung ulang total CR baris tersebut
                    df.at[idx, 'Total_CR'] = sum([df.at[idx, h] for h in hari_list])
                    write_to_gsheets(df)
        else:
            st.warning("Data tidak tersedia.")
    elif pwd != "":
        st.error("Password Salah!")
