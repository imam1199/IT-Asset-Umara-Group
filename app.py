import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.title("Testing App")

# Cek apakah file ada
import os
JSON_FILE = 'dashboard-laptop-it-fe3ec7e15940.json'

if not os.path.exists(JSON_FILE):
    st.error(f"FILE {JSON_FILE} TIDAK DITEMUKAN!")
else:
    st.success("File JSON ditemukan, mencoba koneksi...")
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
        client = gspread.authorize(creds)
        st.write("Koneksi Berhasil!")
    except Exception as e:
        st.error(f"Error: {e}")
