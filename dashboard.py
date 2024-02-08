import streamlit as st

from dim_input import render_dim
from graphics_tab import render_graphics_tab
from session_state_func import create_session_state
from settings_tab import render_settings
from tables_tab import render_tables_tab

st.set_page_config(page_title='Problem Tracker Dashboard',
                   layout='wide',
                   initial_sidebar_state='collapsed')

create_session_state()

if 'password' not in st.session_state:
    st.session_state['password'] = None

col1, col2, col3 = st.columns([1, 1, 1])
if st.session_state['password'] is None:
    with col2:
        with st.form('login'):
            password = st.text_input('Пароль', label_visibility='collapsed', type='password')

            sub = st.form_submit_button('Погнали', use_container_width=True)
            if sub:
                if password == 'passwordtest123':
                    st.session_state['password'] = True
                    st.rerun()
                elif password == 'габариты':
                    st.session_state['password'] = 'dims'
                    st.rerun()
                else:
                    st.error('Ошибка')

if st.session_state['password'] == True:
    tab1, tab2, tab3 = st.tabs(["Таблицы", "Графики и диаграммы", "Настройки"])
    with tab1:
        render_tables_tab()
    with tab2:
        render_graphics_tab()
    with tab3:
        render_settings()

if st.session_state['password'] == 'dims':
    st.session_state['admin_mode'] = True
    render_dim()


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

if st.session_state['admin_mode'] is False:
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
else:
    pass
