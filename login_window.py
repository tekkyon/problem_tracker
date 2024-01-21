import streamlit as st
import time

from cookie_test import cookie_manager


def login_form():
    time.sleep(0.1)
    if st.session_state['authed'] is False:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            with st.form('login form'):
                telegram_id = st.text_input('Telegram ID', disabled=True)
                password = st.text_input('Пароль', type='password')

                enter_button = st.form_submit_button('Войти')

                if enter_button:
                    if password == 'passwordtest123':
                        # cookie_manager.set('authed', True)
                        # cookie_manager.set('telegram_id', telegram_id)
                        st.session_state['authed'] = True
                        st.rerun()
                    else:
                        st.error('Ошибка')
