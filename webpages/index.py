import streamlit as st

pg = st.navigation([
        st.Page('pages/home.py', title='🏠 Home'),
        st.Page('pages/details.py', title='📈 세부 Dashboards'),
        st.Page('pages/ipcountry.py', title='🗺️ IP Country'),
    ])
pg.run()