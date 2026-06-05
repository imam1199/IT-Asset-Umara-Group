import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import os

@st.cache_resource
def get_gspread_client():
    target_file = 'dashboard-laptop-it-fe3ec7e15940.json'
    
    # 1. Mencari lokasi file JSON di seluruh folder proyek
    found_path = None
    for root, dirs, files in os.walk(os.getcwd()):
        if target_file in files:
            found_path = os.path.join(root, target_file)
            break
            
    if not found_path:
        return f"File {target_file} tidak ditemukan di manapun dalam server."
        
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://spreadsheets.google.com/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # 2. Menggunakan path yang ditemukan
        creds = ServiceAccountCredentials.from_json_keyfile_name(found_path, scope)
        return gspread.authorize(creds)
    except Exception as e:
        return f"Gagal otentikasi: {str(e)}"

# ... (Sisa kode untuk menampilkan data sama seperti sebelumnya)
