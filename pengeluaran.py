import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from gspread.utils import column_index_to_string

SPREADSHEET_NAME = "Data Pembelian"
YELLOW = {"red": 1.0, "green": 1.0, "blue": 0.0}

DAFTAR_BARANG = [
    "Bawang Goreng",
    "Daun Sop",
    "Daun Prei",
    "Sawi",
    "Merica",
    "Saos",
    "Kecap",
    "Cuka",
    "Kecap Asin",
    "Cabai",
    "Cappucino",
    "Nutrisari",
    "Teh Tarik",
    "Milo",
    "Jeruk",
    "Sirup",
    "Lemon",
    "Mie Kuning",
    "Mie Hun",
    "Mie Pangsit",
    "Kerupuk Pangsit",
    "Bumbu Pangsit",
    "Ayam Suwir",
    "Ayam Pangsit",
    "Giling Bakso",
    "Plastik Kuah",
    "Plastik Saos/Cabai",
    "Plastik 19",
    "Plastik 24",
    "Karet",
    "Teh Hitam",
    "Teh Hijau",
    "Gula",
    "Telor",
    "Beras",
    "Nipis Madu",
    "Teh Pucuk",
    "Mineral",
    "Fruit Tea",
    "Gas",
    "Tisu",
    "Sedotan",
    "Bawang Putih",
    "Lainnya"
]

def get_client():
    creds_dict = st.secrets["gcp_credentials"]
    creds = Credentials.from_service_account_info(creds_dict)
    return gspread.authorize(creds)

def get_sheet():
    client = get_client()
    spreadsheet = client.open(SPREADSHEET_NAME)
    for ws in spreadsheet.worksheets():
        if ws.title == "Sheet1":
            return ws
    return spreadsheet.add_worksheet("Sheet1", rows=1000, cols=10)

def init_sheet():
    sheet = get_sheet()
    records = sheet.get_all_records()
    if not records:
        sheet.append_row(["Tanggal", "Nama Barang", "Harga (Rp)"])
        sheet.format("A1:C1", {"backgroundColor": YELLOW})
        for col in range(1, 4):
            col_letter = column_index_to_string(col)
            sheet.format(f"{col_letter}:{col_letter}", {"width": 25})

def simpan_data(tanggal, barang, harga):
    sheet = get_sheet()
    records = sheet.get_all_records()
    new_record = {"Tanggal": str(tanggal), "Nama Barang": barang, "Harga (Rp)": int(harga)}
    records.append(new_record)
    records.sort(key=lambda x: x["Tanggal"], reverse=True)

    sheet.clear()
    sheet.append_row(["Tanggal", "Nama Barang", "Harga (Rp)"])
    sheet.format("A1:C1", {"backgroundColor": YELLOW})

    current_date = None
    row = 2
    for rec in records:
        if rec["Tanggal"] != current_date:
            if current_date is not None:
                row += 2
            current_date = rec["Tanggal"]
        sheet.cell(row, 1, rec["Tanggal"])
        sheet.cell(row, 2, rec["Nama Barang"])
        sheet.cell(row, 3, int(rec["Harga (Rp)"]))
        for col in range(1, 4):
            cell = sheet.cell(row, col)
            cell.format({"backgroundColor": YELLOW})
        row += 1

    for col in range(1, 4):
        col_letter = column_index_to_string(col)
        sheet.format(f"{col_letter}:{col_letter}", {"width": 25})

def lihat_data():
    sheet = get_sheet()
    return sheet.get_all_records()

def total_semua():
    records = lihat_data()
    return sum(int(row["Harga (Rp)"]) for row in records)

st.set_page_config(page_title="Catat Pembelian", layout="centered")
st.title("📝 Catatan Pembelian Harian")

sheet = get_sheet()
init_sheet()

st.markdown("---")
st.subheader("📥 Input Data Pembelian")

with st.form("form_beli"):
    tanggal = st.date_input("Tanggal Beli", value=datetime.today())

    barang_input = st.text_input("🔤 Ketik Nama Barang", placeholder="Ketik di sini...")

    if barang_input:
        cocok = [b for b in DAFTAR_BARANG if barang_input.lower() in b.lower()]
        if cocok:
            pilih = st.selectbox("💡 Saran Barang:", cocok, index=0)
            barang = pilih
            st.success(f"✅ Barang ditemukan: **{barang}**")
        else:
            barang = barang_input
            st.info("📝 Barang belum ada di daftar → input manual")
    else:
        barang = ""

    harga = st.number_input("Harga (Rp)", min_value=0, step=1000)
    submit = st.form_submit_button("💾 Simpan")

    if submit:
        if barang.strip() == "":
            st.warning("⚠️ Nama barang tidak boleh kosong!")
        else:
            simpan_data(str(tanggal), barang, int(harga))
            st.success(f"✅ Berhasil! {barang} — Rp {int(harga):,}")

st.markdown("---")
st.subheader("📋 Riwayat Pembelian")

data = lihat_data()
if data:
    for row in data:
        st.markdown(f"📅 **{row['Tanggal']}** | **{row['Nama Barang']}** | Rp **{int(row['Harga (Rp)']):,}**")
    st.markdown(f"### 💵 Total Pengeluaran: **Rp {total_semua():,}**")
else:
    st.info("Belum ada data pembelian.")
