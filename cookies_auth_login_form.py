import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
authenticator.login(fields={'Form name': '',
                            'Username': 'Логин',
                            'Password': 'Пароль',
                            'Login': 'Вход'})


def login_form_func():
    authenticator.login(fields={'Form name': '',
                                'Username': 'Логин',
                                'Password': 'Пароль',
                                'Login': 'Вход'})


def registration_form_func():
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(
            preauthorization=False)
        if email_of_registered_user:
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)
