import streamlit as st

from dashboard_functions import simple_render_user, change_role, change_loc
from config import load_config, Config
from db import read_lexicon, update_lexicon, add_new_worker

db = 'greenea_issues.db'


def render_settings():
    st.session_state['admin_mode'] = st.checkbox('Режим отладки')

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
    marketplace_editor_list = list(read_lexicon().query('purpose == "marketplace"')['value'])

    marketplace_editor_list.insert(0, 'Добавить новый маркетплейс')

    marketplace_editor_selector = st.selectbox('Выбор маркетплейса для редактирования:',
                                               options=marketplace_editor_list,
                                               label_visibility='collapsed')
    mp_edit_t1, mp_edit_t2 = st.columns([5, 1])

    with mp_edit_t1:
        if marketplace_editor_selector != 'Добавить новый маркетплейс':
            new_name_for_marketplace = st.text_input('Новое название',
                                                     value=marketplace_editor_selector)
        else:
            new_name_for_marketplace = st.text_input('Название маркетплейса')

    with mp_edit_t2:
        if marketplace_editor_selector != 'Добавить новый маркетплейс':
            color = read_lexicon().query('value == @marketplace_editor_selector')['color'].iloc[0]
            marketplace_color_picker = st.color_picker('Выбор цвета',
                                                       value=color)
        else:
            marketplace_color_picker = st.color_picker('Выбор цвета',
                                                       value='#FFFFFF')


    save_name = st.button('Сохранить',
                          use_container_width=True)
    if save_name:
        if marketplace_editor_selector != 'Добавить новый маркетплейс':
            update_lexicon(marketplace_editor_selector, new_name_for_marketplace, marketplace_color_picker)
        else:
            pass
        st.success('Успешно')

    st.subheader('Работа с базой данных')
    st.caption('Тут будет раздел с бэкапом базы')
    with open("greenea_issues.db", "rb") as fp:
        btn = st.download_button(
            label="Скачать базу данных",
            data=fp,
            file_name="greenea_issues.db",
            mime="application/octet-stream"
        )


def render_dim_settings():
    dim_settings_col1, dim_settings_col2 = st.columns([2, 3])

    if 'workers_table' not in st.session_state:
        st.session_state['workers_table'] = None

    with dim_settings_col1:
        with st.form('Редактор сотрудников'):
            firstname = st.text_input('Имя')
            lastname = st.text_input('Фамилия')
            position = st.selectbox('Должность',
                                    options=['Сборщик'])

            worker_save_button = st.form_submit_button('Сохранить', disabled=True)

            if worker_save_button:
                add_new_worker(3, firstname, lastname, position)

    with dim_settings_col2:


        if st.session_state['workers_table'] is not None:
            st.dataframe(st.session_state['workers_table'])