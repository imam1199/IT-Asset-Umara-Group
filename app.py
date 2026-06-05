import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import os

# Nama file JSON harus SAMA PERSIS dengan yang ada di GitHub
JSON_FILE = 'dashboard-laptop-it-fe3ec7e15940.json'

@st.cache_resource
def get_gspread_client():
    try:
        # Cek apakah file ada di folder root
        if not os.path.exists(JSON_FILE):
            return f"File {JSON_FILE} tidak ditemukan!"
            
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        # Membaca kredensial dari file JSON fisik
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
        return gspread.authorize(creds)
    except Exception as e:
        return str(e)

st.title("Dashboard IT Asset Umara Group")
client_or_error = get_gspread_client()

if isinstance(client_or_error, str):
    st.error(f"Error Auth: {client_or_error}")
else:
    try:
        # ID Sheet kamu
        sheet = client_or_error.open_by_key("1msf4IK1ZJReQl5f_6VRbVCsGiJXcHUHENto1DqrQwkY").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        if st.button("Simpan Perubahan"):
            sheet.clear()
            sheet.update(range_name='A1', values=[edited_df.columns.tolist()] + edited_df.fillna("").values.tolist())
            st.success("Data berhasil disimpan!")
            st.rerun()
    except Exception as e:
        st.error(f"Error saat mengambil data: {e}")
