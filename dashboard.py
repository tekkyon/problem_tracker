import streamlit as st
import time

from graphics_tab import render_graphics_tab
from login_window import login_form
from session_state_func import create_session_state
from settings_tab import render_settings
from tables_tab import render_tables_tab

st.set_page_config(page_title='Problem Tracker Dashboard',
                   layout='wide',
                   initial_sidebar_state='collapsed')

create_session_state()

login_form()
tab1, tab2, tab3 = st.tabs(["Таблицы", "Графики и диаграммы", "Настройки"])

if st.session_state['authed']:
    # tab1, tab2, tab3 = st.tabs(["Таблицы", "Графики и диаграммы", "Настройки"])
    with tab1:
        render_tables_tab()
    with tab2:
        render_graphics_tab()
    with tab3:
        render_settings()

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)