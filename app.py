import streamlit as st
import pandas as pd
import logging
import sys
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

conn = GSheetsConnection()
df = conn.read(spreadsheet="1vOPqLuwRxvj4Of-t7owwmGvdGE06UjTl9Kve01vpZv0",
               worksheet="DataMember")
print(df.head())

# ======================================================
# LOGGING SETUP (PALING AWAL)
# ======================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("NINJA_APP")
logger.info("🚀 App starting...")

# ======================================================
# KONFIGURASI & KONSTANTA
# ======================================================
st.set_page_config(page_title="Ninja Guild 2025 DB", page_icon="🥷", layout="wide")

SHEET_URL = "1vOPqLuwRxvj4Of-t7owwmGvdGE06UjTl9Kve01vpZv0"
WORKSHEET_NAME = "DataMember"

ADMIN_PASSWORD = "ninja_rahasia"
DAYS_OF_WEEK = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
ADVENT_HEROES = ["Teo", "Kyle", "Yeonhee", "Karma"]

logger.info("📌 Config loaded")
logger.info(f"📄 Spreadsheet ID: {SHEET_URL}")
logger.info(f"📑 Worksheet: {WORKSHEET_NAME}")

# ======================================================
# DATABASE MANAGER
# ======================================================
class DatabaseManager:
    def __init__(self):
        logger.info("🔌 Initializing Google Sheets connection...")
        try:
            self.conn = st.connection("gsheets", type=GSheetsConnection)
            logger.info("✅ GSheets connection initialized")
        except Exception:
            logger.exception("❌ FAILED to initialize GSheets connection")
            raise

    @st.cache_data(ttl=60)
    def load_data(_self):
        logger.info("📥 load_data() started")

        try:
            logger.info("📤 Sending READ request to Google Sheets...")
            df = _self.conn.read(
                spreadsheet=SHEET_URL,
                worksheet=WORKSHEET_NAME
            )

            logger.info(f"📊 Raw data received | rows={len(df)} cols={len(df.columns)}")

            if df.empty:
                logger.warning("⚠️ Sheet returned EMPTY dataframe")
                return pd.DataFrame()

            logger.info("🧹 Cleaning data (drop empty Nama, fillna)...")
            df = df.dropna(subset=["Nama"]).fillna(0)

            logger.info("🔢 Converting numeric columns...")
            numeric_cols = ADVENT_HEROES + DAYS_OF_WEEK + ["Total_Advent", "Total_CR"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
                else:
                    logger.warning(f"⚠️ Column not found: {col}")

            logger.info("✅ load_data() SUCCESS")
            return df

        except Exception:
            logger.exception("❌ load_data() FAILED")
            st.error("Gagal terhubung ke database (lihat logs).")
            return pd.DataFrame()

    def update_data(self, updated_df):
        logger.info("💾 update_data() called")

        try:
            logger.info(f"📤 Writing {len(updated_df)} rows to Google Sheets...")
            self.conn.update(
                spreadsheet=SHEET_URL,
                worksheet=WORKSHEET_NAME,
                data=updated_df
            )

            logger.info("✅ Data successfully written")
            st.cache_data.clear()
            st.success("✅ Database berhasil diperbarui")
            st.rerun()

        except Exception:
            logger.exception("❌ update_data() FAILED")
            st.error("Gagal menyimpan data")

# ======================================================
# APP FLOW
# ======================================================
logger.info("🏗 Creating DatabaseManager...")
db = DatabaseManager()

logger.info("📥 Loading data from database...")
df = db.load_data()

logger.info("🖥 Rendering UI...")
st.title("🏯 Markas Besar Ninja Guild")
st.caption(f"📅 Update Terakhir: {datetime.now().strftime('%d %B %Y %H:%M')}")

if df.empty:
    logger.warning("⚠️ DataFrame empty → stopping app")
    st.warning("⚠️ Data tidak ditemukan atau gagal dimuat.")
    st.stop()

logger.info(f"👥 Data ready | rows={len(df)}")

tabs = st.tabs(["📜 Struktur", "👥 Roster", "🌋 Advent", "🏰 Castle Rush", "⚙️ Admin"])

# ======================================================
# TAB ROSTER
# ======================================================
with tabs[1]:
    st.subheader("Daftar Anggota")
    st.dataframe(
        df[["Nama", "Total_Advent", "Total_CR"]],
        use_container_width=True,
        hide_index=True
    )

# ======================================================
# TAB ADMIN
# ======================================================
with tabs[4]:
    with st.form("admin_login"):
        pwd = st.text_input("Password Admin", type="password")
        login_btn = st.form_submit_button("Masuk")

    if pwd == ADMIN_PASSWORD:
        logger.info("🔓 Admin login SUCCESS")
        st.info("🔓 Mode Admin Aktif")

        target_ninja = st.selectbox("Pilih Ninja", df["Nama"].tolist())
        idx = df[df["Nama"] == target_ninja].index[0]

        mode = st.radio("Kategori Update", ["Advent", "Castle Rush"], horizontal=True)

        if mode == "Advent":
            cols = st.columns(4)
            new_vals = {}
            for i, hero in enumerate(ADVENT_HEROES):
                with cols[i]:
                    new_vals[hero] = st.number_input(hero, value=int(df.at[idx, hero]))

            if st.button("💾 Simpan Data Advent"):
                logger.info(f"💾 Updating Advent data for {target_ninja}")
                for hero, val in new_vals.items():
                    df.at[idx, hero] = val
                df.at[idx, "Total_Advent"] = sum(new_vals.values())
                db.update_data(df)

        else:
            hari = st.selectbox("Pilih Hari", DAYS_OF_WEEK)
            skor = st.number_input(f"Skor {hari}", value=int(df.at[idx, hari]))

            if st.button(f"💾 Simpan Skor {hari}"):
                logger.info(f"💾 Updating CR {hari} for {target_ninja}")
                df.at[idx, hari] = skor
                df.at[idx, "Total_CR"] = df.loc[idx, DAYS_OF_WEEK].sum()
                db.update_data(df)

    elif pwd:
        logger.warning("🚫 Admin login FAILED")
        st.error("❌ Password Salah!")

# ======================================================
# DEBUG PANEL
# ======================================================
with st.expander("🛠 Debug Info"):
    st.write("Rows:", len(df))
    st.write("Columns:", df.columns.tolist())
    st.dataframe(df.head())
