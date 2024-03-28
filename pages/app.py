import time

import pandas as pd
import streamlit as st
import math

from pages.ozon_tab import render_ozon_tab
from pages.session_states import init_session_states
from pages.settings_tab import render_setting_tab
from pages.wb_tab import render_wb_tab

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title='Маркет',
                   layout='wide',
                   initial_sidebar_state='collapsed',
                   page_icon=':seedling:')

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)


init_session_states()

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
    wb_tab, ozon_tab, settings_tab = st.tabs(['Wildberries', 'Ozon', 'Настройки'])

    with wb_tab:
        render_wb_tab()

    with ozon_tab:
        render_ozon_tab()

    with settings_tab:
        render_setting_tab()
