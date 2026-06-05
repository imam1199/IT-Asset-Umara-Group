import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import os

# Menggunakan lokasi absolut agar lebih stabil di Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, 'dashboard-laptop-it-fe3ec7e15940.json')

st.set_page_config(page_title="Dashboard IT Asset", layout="wide")

@st.cache_resource
def get_gspread_client():
    try:
        # Cek apakah file benar-benar ada di path tersebut
        if not os.path.exists(JSON_FILE):
            return f"File tidak ditemukan di path: {JSON_FILE}"
            
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        # Menggunakan creds dari file
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
        return gspread.authorize(creds)
    except Exception as e:
        return f"Gagal otentikasi: {str(e)}"

st.title("Dashboard IT Asset Umara Group")

client_or_error = get_gspread_client()

if isinstance(client_or_error, str):
    st.error(f"Error Auth: {client_or_error}")
else:
    try:
        # Buka sheet
        sheet = client_or_error.open_by_key("1msf4IK1ZJReQl5f_6VRbVCsGiJXcHUHENto1DqrQwkY").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Editor data
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        if st.button("Simpan Perubahan"):
            # Update data ke sheets
            sheet.clear()
            # Menyiapkan data untuk di-update (header + data)
            values = [edited_df.columns.tolist()] + edited_df.fillna("").values.tolist()
            sheet.update(range_name='A1', values=values)
            st.success("Data berhasil disimpan!")
            st.rerun()
            
    except Exception as e:
        st.error(f"Error saat mengambil data: {e}")
