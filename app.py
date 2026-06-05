import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import os

st.set_page_config(page_title="Dashboard IT Asset", layout="wide")

@st.cache_resource
def get_gspread_client():
    try:
        # Lokasi file JSON yang sudah ada di folder root
        json_file = 'dashboard-laptop-it-fe3ec7e15940.json'
        
        if not os.path.exists(json_file):
            return "File JSON tidak ditemukan!"
            
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        
        # Menggunakan oauth2client yang lebih standar untuk gspread
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
        return gspread.authorize(creds)
    except Exception as e:
        return str(e)

st.title("Dashboard IT Asset Umara Group")
client_or_error = get_gspread_client()

if isinstance(client_or_error, str):
    st.error(f"Error Auth: {client_or_error}")
elif client_or_error:
    try:
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
