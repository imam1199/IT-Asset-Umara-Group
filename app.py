import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

st.title("Dashboard IT Asset Umara Group")

# Konfigurasi koneksi
JSON_FILE = 'dashboard-laptop-it-fe3ec7e15940.json'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive', 'https://spreadsheets.google.com/spreadsheets']

@st.cache_resource
def get_data():
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1msf4IK1ZJReQl5f_6VRbVCsGiJXcHUHENto1DqrQwkY").sheet1
    return sheet

try:
    sheet = get_data()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    # Menampilkan data agar bisa diedit
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Simpan Perubahan"):
        # Menghapus data lama dan menulis data baru
        sheet.clear()
        sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
        st.success("Data berhasil disimpan!")
        st.rerun()
        
except Exception as e:
    st.error(f"Error: {e}")
