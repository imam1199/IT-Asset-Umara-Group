import streamlit as st
import gspread
import pandas as pd
from google.oauth2 import service_account
import json

st.set_page_config(page_title="Dashboard IT Asset", layout="wide")
st.title("Dashboard IT Asset Umara Group")

JSON_FILE = 'dashboard-laptop-it-fe3ec7e15940.json'

SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'  # ← tambah /auth/
]

@st.cache_resource
def get_client():
    with open(JSON_FILE, 'r') as f:
        service_account_info = json.load(f)
    
    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )
    return gspread.authorize(creds)

try:
    client = get_client()
    sheet = client.open_by_key("1msf4IK1ZJReQl5f_6VRbVCsGiJXcHUHENto1DqrQwkY").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if st.button("Simpan Perubahan"):
        sheet.clear()
        values = [edited_df.columns.values.tolist()] + edited_df.fillna("").values.tolist()
        sheet.update(range_name='A1', values=values)
        st.success("Data berhasil disimpan!")
        st.rerun()

except Exception as e:
    st.error(f"Error: {e}")
