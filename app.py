import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
from io import BytesIO
import json

st.set_page_config(page_title="Dashboard IT Asset", layout="wide")
st.title("Dashboard IT Asset Umara Group")

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SHEET_ID = "1msf4IK1ZJReQl5f_6VRbVCsGiJXcHUHENto1DqrQwkY"

@st.cache_resource
def get_client():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(creds)

@st.cache_data(ttl=30)
def load_data():
    client = get_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data), sheet

def save_data(df):
    client = get_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    sheet.clear()
    values = [df.columns.tolist()] + df.fillna("").values.tolist()
    sheet.update(range_name='A1', values=values)
    st.cache_data.clear()

try:
    df, sheet = load_data()

    # ── TABS ──
    tab1, tab2, tab3 = st.tabs(["📋 Data", "📊 Chart", "➕ Tambah / Edit / Hapus"])

    # ════════════════════════════════
    # TAB 1 — DATA + FILTER + EXPORT
    # ════════════════════════════════
    with tab1:
        st.subheader("Filter Data")
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_model = st.multiselect("Model", options=sorted(df["Model"].dropna().unique()))
        with col2:
            filter_status = st.multiselect("Status", options=sorted(df["Status"].dropna().unique()))
        with col3:
            filter_bu = st.multiselect("Bu Owner", options=sorted(df["Bu Owner"].dropna().unique()))

        search = st.text_input("🔍 Cari (nama user, serial number, dll)")

        filtered = df.copy()
        if filter_model:
            filtered = filtered[filtered["Model"].isin(filter_model)]
        if filter_status:
            filtered = filtered[filtered["Status"].isin(filter_status)]
        if filter_bu:
            filtered = filtered[filtered["Bu Owner"].isin(filter_bu)]
        if search:
            filtered = filtered[filtered.apply(
                lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1
            )]

        st.dataframe(filtered, use_container_width=True)
        st.caption(f"Total: {len(filtered)} data")

        # Export
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                filtered.to_excel(writer, index=False)
            st.download_button("📥 Export Excel", buffer.getvalue(),
                               file_name="it_asset.xlsx",
                               mime="application/vnd.ms-excel")
        with col_exp2:
            csv = filtered.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export CSV", csv,
                               file_name="it_asset.csv", mime="text/csv")

    # ════════════════════════════════
    # TAB 2 — CHART
    # ════════════════════════════════
    with tab2:
        st.subheader("Statistik Asset")

        c1, c2 = st.columns(2)
        with c1:
            status_count = df["Status"].value_counts().reset_index()
            status_count.columns = ["Status", "Jumlah"]
            fig1 = px.pie(status_count, names="Status", values="Jumlah",
                          title="Distribusi Status Asset", hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            model_count = df["Model"].value_counts().reset_index()
            model_count.columns = ["Model", "Jumlah"]
            fig2 = px.bar(model_count, x="Model", y="Jumlah",
                          title="Jumlah per Model", color="Jumlah")
            st.plotly_chart(fig2, use_container_width=True)

        bu_count = df["Bu Owner"].value_counts().reset_index()
        bu_count.columns = ["Bu Owner", "Jumlah"]
        fig3 = px.bar(bu_count, x="Bu Owner", y="Jumlah",
                      title="Asset per BU", color="Bu Owner")
        st.plotly_chart(fig3, use_container_width=True)

    # ════════════════════════════════
    # TAB 3 — TAMBAH / EDIT / HAPUS
    # ════════════════════════════════
    with tab3:
        action = st.radio("Pilih Aksi", ["✏️ Edit Data", "➕ Tambah Data", "🗑️ Hapus Data"],
                          horizontal=True)

        # ── EDIT ──
        if action == "✏️ Edit Data":
            st.subheader("Edit Data")
            edited = st.data_editor(df, num_rows="fixed", use_container_width=True)
            if st.button("💾 Simpan Perubahan"):
                save_data(edited)
                st.success("Data berhasil disimpan!")
                st.rerun()

        # ── TAMBAH ──
        elif action == "➕ Tambah Data":
            st.subheader("Tambah Data Baru")
            new_row = {}
            cols = st.columns(3)
            for i, col in enumerate(df.columns):
                with cols[i % 3]:
                    new_row[col] = st.text_input(col)

            if st.button("➕ Tambah"):
                new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(new_df)
                st.success("Data berhasil ditambahkan!")
                st.rerun()

        # ── HAPUS ──
        elif action == "🗑️ Hapus Data":
            st.subheader("Hapus Data")
            st.dataframe(df, use_container_width=True)
            row_idx = st.number_input("Nomor baris yang mau dihapus (mulai dari 0)",
                                      min_value=0, max_value=len(df)-1, step=1)
            st.warning(f"Akan menghapus: {df.iloc[int(row_idx)].to_dict()}")
            if st.button("🗑️ Hapus"):
                new_df = df.drop(index=int(row_idx)).reset_index(drop=True)
                save_data(new_df)
                st.success("Data berhasil dihapus!")
                st.rerun()

except Exception as e:
    import traceback
    st.error(f"Error: {e}")
    st.code(traceback.format_exc())
