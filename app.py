import streamlit as st
import gspread
import pandas as pd
from google.oauth2 import service_account

st.set_page_config(page_title="Dashboard IT Asset", layout="wide")
st.title("Dashboard IT Asset Umara Group")

# Konfigurasi
JSON_FILE = 'dashboard-laptop-it-fe3ec7e15940.json'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/spreadsheets']

@st.cache_resource
def get_data():
    # Menggunakan google-auth yang lebih stabil untuk sinkronisasi waktu
    creds = service_account.Credentials.from_service_account_file(JSON_FILE, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1msf4IK1ZJReQl5f_6VRbVCsGiJXcHUHENto1DqrQwkY").sheet1
    return sheet

try:
    sheet = get_data()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Simpan Perubahan"):
        # sheet.update() versi gspread terbaru pakai format ini:
        sheet.clear()
        values = [edited_df.columns.values.tolist()] + edited_df.fillna("").values.tolist()
        sheet.update(range_name='A1', values=values)
        st.success("Data berhasil disimpan!")
        st.rerun()
        
except Exception as e:
    st.error(f"Error: {e}")
