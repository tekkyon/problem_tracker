import streamlit as st
import time
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from session_state_func import create_session_state

st.set_page_config(page_title='Dashboard',
                   layout='wide',
                   initial_sidebar_state='collapsed',
                   page_icon=':seedling:')

create_session_state()

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

my_bar = st.progress(0, text='')

for percent_complete in range(100):
    time.sleep(0.001)
    my_bar.progress(percent_complete + 1, text='')
time.sleep(1)
my_bar.empty()

_, login_col, _ = st.columns([1, 1, 1])


def unauthenticated_menu():
    st.sidebar.page_link("app.py", label="Вход")
    with login_col:
        authenticator.login(fields={'Form name': '',
                                    'Username': 'Логин',
                                    'Password': 'Пароль',
                                    'Login': 'Вход'})

def authenticated_menu():
    st.sidebar.page_link("app.py", label="Сменить профиль")
    st.sidebar.page_link("pages/dims.py", label="Габариты")

if st.session_state["authentication_status"] is None or st.session_state["authentication_status"] is False:
    unauthenticated_menu()
else:
    authenticated_menu()