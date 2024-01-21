import streamlit as st

from dashboard_functions import simple_render_user, change_role, change_loc
from config import load_config, Config
from db import read_lexicon

db = 'greenea_issues.db'


def render_settings():
    st.subheader('Настройки доступа')
    config: Config = load_config()
    st.text_input(label='Токен телеграм бота',
                  value=config.tg_bot.token,
                  disabled=True)

    users_df_columns = ['username', 'user_id', 'role', 'location']
    users_df = simple_render_user(db, 'users', users_df_columns, list_mode=True, users='all')

    role_options = ['admin',
                    'pending',
                    'user']

    location_options = ['Офис',
                        'Склад']

    column_config = {'username': st.column_config.TextColumn('Имя пользователя'),
                     'user_id': st.column_config.TextColumn('Telegram ID'),
                     'role': st.column_config.SelectboxColumn('Авторизация',
                                                              options=role_options,
                                                              required=True),
                     'location': st.column_config.SelectboxColumn('Отдел',
                                                                  options=location_options,
                                                                  required=True)
                     }
    with st.form('role_form'):
        user_editor = st.data_editor(users_df,
                                     column_config=column_config,
                                     key='user_editor',
                                     use_container_width=True,
                                     hide_index=True,
                                     disabled=['username',
                                               'user_id'])

        save = st.form_submit_button('Сохранить изменения')
        if save:
            list_of_edited_users = list(st.session_state["user_editor"]['edited_rows'].keys())
            for user in list_of_edited_users:
                user_id = users_df['user_id'].iloc[user]
                if "role" in st.session_state["user_editor"]['edited_rows'][user]:
                    role = st.session_state["user_editor"]['edited_rows'][user]["role"]
                    change_role(user_id=user_id, role=role)
                if "location" in st.session_state["user_editor"]['edited_rows'][user]:
                    location = st.session_state["user_editor"]['edited_rows'][user]["location"]
                    change_loc(user_id=user_id, location=location)

    st.subheader('Настройки маркетплейсов и тегов')
    st.caption('Здесь можно будет добавить иные названия маркетов и дополнительные теги для них')
    st.dataframe(read_lexicon().query('purpose == "marketplace"')['value'])

    st.subheader('Работа с базой данных')
    st.caption('Тут будет раздел с бэкапом базы')
    with open("greenea_issues.db", "rb") as fp:
        btn = st.download_button(
            label="Скачать базу данных",
            data=fp,
            file_name="greenea_issues.db",
            mime="application/octet-stream"
        )

    st.subheader('Настройки профиля')
    st.caption('Здесь будут настройки профиля')
