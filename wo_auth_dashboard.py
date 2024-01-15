import datetime
import sqlite3

import pandas as pd
import streamlit as st
import yaml
# from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader

from config import load_config, Config

import altair as alt

from dashboard_functions import render_default_dataframe, render_users, change_role, simple_render_user
from lexicon import month_dict, lexicon_dict, numerical_month_dict

import seaborn as sns

if 'stats_selector' not in st.session_state:
    st.session_state['stats_selector'] = None

if 'filter_selector' not in st.session_state:
    st.session_state['filter_selector'] = None

if 'day_selector' not in st.session_state:
    st.session_state['day_selector'] = None

if 'result_df' not in st.session_state:
    st.session_state['result_df'] = None

if 'period_selector' not in st.session_state:
    st.session_state['period_selector'] = None

if 'day_1' not in st.session_state:
    st.session_state['day_1'] = datetime.date(2022, 12, 13)

if 'day_2' not in st.session_state:
    st.session_state['day_2'] = datetime.date.today()

if 'metric_state' not in st.session_state:
    st.session_state['metric_state'] = None

if 'total_problems' not in st.session_state:
    st.session_state['total_problems'] = None

if 'period_problems' not in st.session_state:
    st.session_state['period_problems'] = None

if 'defect_month_before' not in st.session_state:
    st.session_state['defect_month_before'] = None

if 'package_month_before' not in st.session_state:
    st.session_state['package_month_before'] = None

if 'total_month_before' not in st.session_state:
    st.session_state['total_month_before'] = None

if 'delta_option' not in st.session_state:
    st.session_state['delta_option'] = None

if 'graph_selector' not in st.session_state:
    st.session_state['graph_selector'] = None

if 'graph_period_selector' not in st.session_state:
    st.session_state['graph_period_selector'] = None

if 'graph_radio_selector' not in st.session_state:
    st.session_state['graph_radio_selector'] = 'Линейный график'

if 'authed' not in st.session_state:
    st.session_state['authed'] = None

if 'sku_radio_selector' not in st.session_state:
    st.session_state['sku_radio_selector'] = 'По типу проблемы'

# with open('auth_info.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)

db = 'greenea_issues.db'

st.set_page_config(page_title='Problem Tracker Dashboard',
                   layout='wide',
                   initial_sidebar_state='collapsed')

# authenticator = Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days'],
#     config['preauthorized']
# )

# name, authentication_status, username = authenticator.login('Вход в дашборд', 'main')


first_date = datetime.date(2022, 12, 13)
today = datetime.datetime.now()

stat_options = ['Общая таблица',
                'По типу проблемы',
                'По артикулу']

filter_options = ['За все время',
                  'По месяцам']

columns_list = ['sku_number',
                'marketplace',
                'date',
                'type',
                'comment']

if st.session_state['authed'] is None:
    log_c1, log_c2, log_c3 = st.columns([3, 2, 3])
    with log_c2:
        with st.form('login_form'):
            password_input = st.text_input(label='Пароль для доступа')

            sub_c1, sub_c2, sub_c3 = st.columns([1, 1, 1])
            with sub_c2:
                submitted = st.form_submit_button("Submit")
            if submitted:
                if password_input == 'passwordtest123':
                    st.session_state['authed'] = True
                    st.rerun()
                else:
                    st.error('Введен неверный пароль')

elif st.session_state['authed']:
    tab1, tab2, tab3 = st.tabs(["Таблицы", "Графики и диаграммы", "Настройки"])
    with tab1:
        col1, col2 = st.columns([1, 4])
        with col1:

            st.session_state['stats_selector'] = st.selectbox(
                'Какой тип статистики интересует?',
                options=stat_options
            )

            if st.session_state['stats_selector'] != 'Общая таблица':
                st.session_state['period_selector'] = st.selectbox(
                    'За какой период?',
                    options=filter_options
                )
                if st.session_state['period_selector'] == 'По дням':
                    with st.form("my_form"):
                        st.session_state['day_selector'] = st.date_input('Выбор дней:',
                                                                         (first_date, today),
                                                                         min_value=first_date,
                                                                         format="DD.MM.YYYY")
                        submitted = st.form_submit_button("Применить фильтр")
                        if submitted:
                            st.session_state['day_1'] = st.session_state['day_selector'][0]
                            st.session_state['day_2'] = st.session_state['day_selector'][1]
            else:
                with st.form("my_form"):
                    st.session_state['day_selector'] = st.date_input('Выбор дней:',
                                                                     (first_date, today),
                                                                     min_value=first_date,
                                                                     format="DD.MM.YYYY")
                    submitted = st.form_submit_button("Применить фильтр")
                    if submitted:
                        st.session_state['day_1'] = st.session_state['day_selector'][0]
                        st.session_state['day_2'] = st.session_state['day_selector'][1]

        if st.session_state['stats_selector'] == 'Общая таблица':

            df = render_default_dataframe(db, 'main', columns_list)
            df['type'] = df['type'].apply(lambda x: lexicon_dict[x])
            df['marketplace'] = df['marketplace'].apply(lambda x: lexicon_dict[x])
            df.rename(columns={'type': 'Тип проблемы',
                               'date': 'Дата',
                               'marketplace': 'Маркетплейс',
                               'sku_number': 'Артикул',
                               'comment': 'Комментарий'}, inplace=True)
            df['Дата'] = pd.to_datetime(df['Дата']).dt.date
            st.session_state['total_problems'] = df.shape[0]
            df = df.loc[
                (df['Дата'] >= st.session_state['day_1']) & (df['Дата'] < st.session_state['day_2'])]
            df['Дата'] = pd.to_datetime(df['Дата']).dt.date.apply(lambda x: x.strftime('%d/%m/%Y'))
            st.session_state['period_problems'] = df.shape[0]
            st.session_state['result_df'] = df

            with col2:
                m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
                with m_col1:
                    st.metric(label="Общее количество проблем",
                              value=st.session_state['total_problems'])
                with m_col2:
                    st.metric(label="Количество за выбранный период",
                              value=st.session_state['period_problems'])


        elif st.session_state['stats_selector'] == 'Статистика по группам артикулов':
            st.header('Статистика по группам артикулов')
            with sqlite3.connect(db) as con:
                sql_query = pd.read_sql('SELECT * FROM main', con, parse_dates=['date'])
                df = pd.DataFrame(sql_query, columns=['sku', 'sku_number', 'marketplace', 'date', 'type', 'comment'])
                df.rename(columns={'type': 'type_of_problem'}, inplace=True)

                group1 = [x for x in range(100, 200)]
                result = df.query('sku_number == @group1').groupby(
                    by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                    {'sku_number': 'count'}).reset_index()

                st.subheader('Группа артикулов 100-199')
                st.dataframe(result, use_container_width=True, hide_index=True)

                group2 = [x for x in range(200, 300)]
                result = df.query('sku_number == @group2').groupby(
                    by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                    {'sku_number': 'count'}).reset_index()

                st.subheader('Группа артикулов 200-299')
                st.dataframe(result, use_container_width=True, hide_index=True)

                group3 = [x for x in range(300, 400)]
                result = df.query('sku_number == @group3').groupby(
                    by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                    {'sku_number': 'count'}).reset_index()

                st.subheader('Группа артикулов 300-399')
                st.dataframe(result, use_container_width=True, hide_index=True)

                group4 = [400, 401, 402, 403, 404, 468, 473]
                result = df.query('sku_number == @group4').groupby(
                    by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                    {'sku_number': 'count'}).reset_index()

                st.subheader('Группа артикулов 400-499')
                st.dataframe(result, use_container_width=True, hide_index=True)

                group5 = [413, 416, 418, 422, 423, 427, 446, 447, 448, 449, 450, 451, 452, 454, 455, 457, 460, 464]
                result = df.query('sku_number == @group5').groupby(
                    by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                    {'sku_number': 'count'}).reset_index()

                st.subheader('Группа артикулов ГЛТ 411-513')
                st.dataframe(result, use_container_width=True, hide_index=True)

                group6 = [x for x in range(500, 600)]
                result = df.query('sku_number == @group6').groupby(
                    by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                    {'sku_number': 'count'}).reset_index()

                st.subheader('Группа артикулов ГЛТ 500-600')
                st.dataframe(result, use_container_width=True, hide_index=True)

        elif st.session_state['stats_selector'] == 'По типу проблемы':

            if st.session_state['period_selector'] == 'За все время':
                df = render_default_dataframe(db, 'main', columns_list)
                df.rename(columns={'type': 'type_of_problem'}, inplace=True)

                defect_df = df.query('type_of_problem == "defect"').groupby(
                    by=['marketplace']).size().reset_index()

                bad_package_df = df.query('type_of_problem == "bad_package"').groupby(
                    by=['marketplace']).size().reset_index()
                with col2:
                    df1 = defect_df.T.rename(index={0: 'Проблема с товаром'})
                    df2 = bad_package_df.T.iloc[1:].rename(index={0: 'Проблема со сборкой'})
                    new = pd.concat([df1, df2])
                    new.columns = new.iloc[0]
                    new.columns = list(map(lambda x: lexicon_dict[x], new.columns))
                    new = new.iloc[1:]
                    st.dataframe(new, hide_index=False, use_container_width=True)

                st.session_state['result_df'] = None

            if st.session_state['period_selector'] == 'По месяцам':
                with col1:
                    st.session_state['delta_option'] = st.radio(label='type of delta',
                                                                options=['Абсолютная разница', 'Разница в процентах'],
                                                                label_visibility='hidden')

                df = render_default_dataframe(db, 'main', columns_list)
                df.rename(columns={'type': 'type_of_problem'}, inplace=True)
                df['month&year'] = df['date'].dt.to_period('M')
                df['year'] = df['date'].dt.year
                list_of_markets = list(df['marketplace'].unique())

                with col2:
                    list_of_month = []
                    for date in df['month&year'].unique():
                        month_df = pd.DataFrame(columns=['Маркетплейс', 'Проблема с товаром', 'Проблема со сборкой'])

                        st.subheader(f'{numerical_month_dict[date.month]} {str(date.year)}')

                        temp = df.loc[(df['date'].dt.month == date.month) & (df['date'].dt.year == date.year)]
                        for market in list_of_markets:
                            qny_defect = temp.query(f'type_of_problem == "defect" & marketplace == "{market}"').shape[0]

                            bad_package = \
                                temp.query(f'type_of_problem == "bad_package" & marketplace == "{market}"').shape[0]

                            data = {'Маркетплейс': lexicon_dict[market],
                                    'Проблема с товаром': qny_defect,
                                    'Проблема со сборкой': bad_package}

                            month_df.loc[len(month_df)] = data

                        total_this_month = month_df['Проблема с товаром'].sum() + month_df['Проблема со сборкой'].sum()
                        defect_this_month = month_df['Проблема с товаром'].sum()
                        package_this_month = month_df['Проблема со сборкой'].sum()
                        # if st.session_state['total_month_before'] == 0:

                        m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
                        with m_col1:
                            if st.session_state['total_month_before'] is None:
                                if st.session_state['delta_option'] == 'Абсолютная разница':
                                    delta = 0
                                else:
                                    delta = '0%'

                            else:
                                if st.session_state['delta_option'] == 'Абсолютная разница':
                                    delta = int(total_this_month - st.session_state['total_month_before'])
                                else:
                                    try:
                                        delta = round(float(
                                            (total_this_month - st.session_state['total_month_before']) /
                                            st.session_state[
                                                'total_month_before'] * 100), 2)
                                        delta = f'{delta}%'
                                    except:
                                        delta = '0%'

                            st.metric('Количество проблем за период',
                                      total_this_month,
                                      delta,
                                      delta_color='inverse')
                            st.session_state['total_month_before'] = total_this_month

                        with m_col2:
                            if st.session_state['defect_month_before'] is None:
                                if st.session_state['delta_option'] == 'Абсолютная разница':
                                    delta = 0
                                else:
                                    delta = '0%'

                            else:
                                if st.session_state['delta_option'] == 'Абсолютная разница':
                                    delta = int(defect_this_month - st.session_state['defect_month_before'])
                                else:
                                    try:
                                        delta = round(float(
                                            (defect_this_month - st.session_state['defect_month_before']) /
                                            st.session_state['defect_month_before'] * 100), 2)
                                        delta = f'{delta}%'
                                    except:
                                        delta = '0%'

                            st.metric('Проблемы с товаром',
                                      defect_this_month,
                                      delta,
                                      delta_color='inverse')
                            st.session_state['defect_month_before'] = defect_this_month

                        with m_col3:
                            if st.session_state['package_month_before'] is None:
                                if st.session_state['delta_option'] == 'Абсолютная разница':
                                    delta = 0
                                else:
                                    delta = '0%'

                            else:
                                if st.session_state['delta_option'] == 'Абсолютная разница':
                                    delta = int(package_this_month - st.session_state['package_month_before'])
                                else:
                                    try:
                                        delta = round(float(
                                            (package_this_month - st.session_state['package_month_before']) /
                                            st.session_state['package_month_before'] * 100), 2)
                                        delta = f'{delta}%'
                                    except:
                                        delta = '0%'

                            st.metric('Проблемы со сборкой',
                                      package_this_month,
                                      delta,
                                      delta_color='inverse')
                            st.session_state['package_month_before'] = package_this_month

                        st.table(month_df.set_index('Маркетплейс'))

                st.session_state['defect_month_before'] = None

                st.session_state['package_month_before'] = None

                st.session_state['total_month_before'] = None

            if st.session_state['period_selector'] == 'По дням':
                st.session_state['result_df'] = None

        elif st.session_state['stats_selector'] == 'По артикулу':
            df = render_default_dataframe(db, 'main', columns_list)
            df.rename(columns={'type': 'type_of_problem'}, inplace=True)

            if st.session_state['period_selector'] == 'За все время':
                with col1:
                    st.session_state['sku_radio_selector'] = st.radio('Отобразить:',
                                                                      options=['По типу проблемы',
                                                                               'По маркетплейсам'])

                if st.session_state['sku_radio_selector'] == 'По типу проблемы':
                    defect_df = df.query('type_of_problem == "defect"').groupby(
                        by=['sku_number']).size().reset_index()

                    bad_package_df = df.query('type_of_problem == "bad_package"').groupby(
                        by=['sku_number']).size().reset_index()

                    agg_df = defect_df.merge(bad_package_df, on='sku_number')
                    agg_df.rename(columns={'sku_number': 'Артикул',
                                           '0_x': 'Проблемы с товаром',
                                           '0_y': 'Проблемы со сборкой'},
                                  inplace=True)
                    agg_df = agg_df.set_index(['Артикул'])
                    with col2:
                        st.dataframe(agg_df, use_container_width=True, hide_index=False)

                    st.session_state['result_df'] = None

                if st.session_state['sku_radio_selector'] == 'По маркетплейсам':
                    with col2:
                        list_of_markets = list(df['marketplace'].unique())
                        result_df = pd.DataFrame()
                        for market in list_of_markets:
                            market_df = df.query(f'marketplace == "{market}"')
                            market_df = market_df.groupby(by='sku_number').agg(
                                market=('comment', 'count')).reset_index()
                            market_df.rename(columns={'market': lexicon_dict[market]}, inplace=True)
                            market_df.set_index('sku_number', inplace=True)

                            if len(result_df) == 0:
                                result_df = market_df
                            else:
                                result_df = pd.merge(result_df, market_df, how='outer', on='sku_number')

                        result_df = result_df.fillna(0)
                        result_df = result_df.reset_index().rename(columns={'sku_number':'Артикул'})
                        result_df.set_index('Артикул', inplace=True)

                        st.dataframe(result_df, use_container_width=True)
                        st.session_state['result_df'] = None

            if st.session_state['period_selector'] == 'По месяцам':
                st.session_state['result_df'] = None

            if st.session_state['period_selector'] == 'По дням':
                st.session_state['result_df'] = None

        with col2:
            if st.session_state['result_df'] is not None:
                st.dataframe(st.session_state['result_df'], hide_index=True, use_container_width=True)
                # st.write(st.session_state['result_df'].to_html(index=False), unsafe_allow_html=True)
    with tab2:
        df = render_default_dataframe(db, 'main', columns_list)
        df['type'] = df['type'].apply(lambda x: lexicon_dict[x])
        df['marketplace'] = df['marketplace'].apply(lambda x: lexicon_dict[x])
        df.rename(columns={'type': 'Тип проблемы',
                           'date': 'Дата',
                           'marketplace': 'Маркетплейс',
                           'sku_number': 'Артикул',
                           'comment': 'Комментарий'}, inplace=True)

        df = df.drop(columns=['Комментарий']).sort_values(by='Дата')

        st.session_state['graph_selector'] = st.selectbox(label='Какой график построить?',
                                                          options=['По типу проблемы',
                                                                   'Доля по маркетплейсам'])

        # st.session_state['graph_radio_selector'] = st.radio(label='Тип графика',
        #                                                     options=['Линейный график',
        #                                                              'Столбчатый график'],
        #                                                     horizontal=True)

        st.session_state['graph_period_selector'] = st.selectbox(label='Периодичность',
                                                                 options=['По дням',
                                                                          'По месяцам'])

        if st.session_state['graph_period_selector'] == 'По месяцам':
            frequency_graph = 'M'
        elif st.session_state['graph_period_selector'] == 'По дням':
            frequency_graph = 'D'

        if st.session_state['graph_selector'] == 'По типу проблемы':

            df = df.groupby(by=[pd.Grouper(key='Дата', freq=frequency_graph), 'Тип проблемы']).agg(
                {'Артикул': 'count'}).reset_index()
            df.rename(columns={'Артикул': 'Число проблем'}, inplace=True)

            if st.session_state['graph_radio_selector'] == 'Линейный график':
                st.line_chart(data=df,
                              x='Дата',
                              y='Число проблем',
                              color='Тип проблемы',
                              use_container_width=True)

        if st.session_state['graph_selector'] == 'Доля по маркетплейсам':

            df = df.groupby(by=[pd.Grouper(key='Дата', freq=frequency_graph), 'Маркетплейс']).agg(
                {'Артикул': 'count'}).reset_index()
            df.rename(columns={'Артикул': 'Число проблем'}, inplace=True)

            if st.session_state['graph_radio_selector'] == 'Линейный график':
                st.line_chart(data=df,
                              x='Дата',
                              y='Число проблем',
                              color='Маркетплейс',
                              use_container_width=True)

    with tab3:

        st.subheader('Настройки доступа')
        config: Config = load_config()
        st.text_input(label='Токен телеграм бота',
                      value=config.tg_bot.token,
                      disabled=True)

        users_df_columns = ['username', 'user_id', 'role']
        users_df = simple_render_user(db, 'users', users_df_columns, list_mode=True, users='all')

        role_options = ['admin',
                        'pending',
                        'user']

        column_config = {'username': st.column_config.TextColumn('Имя пользователя'),
                         'user_id': st.column_config.TextColumn('Telegram ID'),
                         'role': st.column_config.SelectboxColumn('Авторизация',
                                                                  options=role_options,
                                                                  required=True, )}
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
                    role = st.session_state["user_editor"]['edited_rows'][user]["role"]
                    change_role(user_id=user_id, role=role)

        st.subheader('Настройки маркетплейсов и тегов')
        st.caption('Здесь можно будет добавить иные названия маркетов и дополнительные теги для них')

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

st.divider()

# elif st.session_state["authentication_status"] is False:
#     st.error('Username/password is incorrect')
#
# elif st.session_state["authentication_status"] is None:
#     st.warning('Please enter your username and password')

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
