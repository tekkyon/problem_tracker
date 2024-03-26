import streamlit as st

from b2b_tab import render_b2b_tab
from dim_input import render_dim
from graphics_tab import render_graphics_tab
from session_state_func import create_session_state
from settings_tab import render_settings
from refactored_tables_tab import render_tables_tab
from cookies_auth_login_form import *
import time
import extra_streamlit_components as stx
from streamlit.errors import DuplicateWidgetID, StreamlitAPIException

from stickers import render_sticker_df

try:
    st.set_page_config(page_title='Dashboard',
                       layout='wide',
                       initial_sidebar_state='collapsed',
                       page_icon=':seedling:')
except (DuplicateWidgetID, StreamlitAPIException):
    st.rerun()

create_session_state()

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

if 'query_params' not in st.session_state:
    st.session_state['query_params'] = None

if st.query_params is not None:
    st.session_state['query_params'] = st.query_params


def update_creds():
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)


try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    if st.session_state['first_load']:
        my_bar = st.progress(0, text='')

        for percent_complete in range(100):
            time.sleep(0.001)
            my_bar.progress(percent_complete + 1, text='')
        time.sleep(1)
        my_bar.empty()

    if st.session_state["authentication_status"] is None:
        login_col1, login_col2, login_col3 = st.columns([1, 1, 1])
        with login_col2:
            authenticator.login(fields={'Form name': '',
                                        'Username': 'Логин',
                                        'Password': 'Пароль',
                                        'Login': 'Вход'})

    elif st.session_state["authentication_status"] is False:
        st.toast('Что-то пошло не так :(')
        login_col1, login_col2, login_col3 = st.columns([1, 1, 1])
        with login_col2:
            authenticator.login(fields={'Form name': '',
                                        'Username': 'Логин',
                                        'Password': 'Пароль',
                                        'Login': 'Вход'})

    if st.session_state["authentication_status"]:
        st.session_state['first_load'] = False
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Таблицы",
                                                "Графики и диаграммы",
                                                'Брак B2B',
                                                'Габариты',
                                                      'Этикетки',
                                                "Настройки/Логи"])
        with tab1:
            render_tables_tab()
        with tab2:
            render_graphics_tab()
        with tab3:
            render_b2b_tab()
        with tab4:
            render_dim()
        with tab5:
            render_sticker_df()
        with tab6:
            render_settings()

# except KeyError as error:
#     st.info(error)
#     st.error('Ошибка cookies. Необходимо удалить cookies связанные с дашбордом в настройках браузера.')

except ModuleNotFoundError as error:
    st.error('Ошибка импорта модулей :(')
