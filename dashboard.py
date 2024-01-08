import datetime
import sqlite3

import pandas as pd
import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader

from lexicon import month_dict, lexicon_dict

with open('auth_info.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

db = 'greenea_issues_backup.db'

st.set_page_config(page_title='Problem Tracker Dashboard',
                   layout='wide',
                   initial_sidebar_state='collapsed')

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

stat_options = ['Просмотреть базу данных',
                'Статистика по типу проблемы по месяцам',
                'Общая статистика по артикулу',
                'Статистика по маркетам',
                'Статистика по группам артикулов']

filter_options = ['Без фильтра',
                  'По дням']

if st.session_state["authentication_status"]:
    st.session_state['stats_selector'] = st.selectbox(
        'Какой тип статистики интересует?',
        options=stat_options
    )

    st.divider()
    if st.session_state['stats_selector'] == 'Просмотреть базу данных':
        st.header('Вся бд')

        st.session_state['filter_selector'] = st.selectbox(
            'Какой фильтр применить?',
            options=filter_options
        )

        if st.session_state['filter_selector'] == 'Без фильтра':
            with sqlite3.connect(db) as con:
                sql_query = pd.read_sql('SELECT * FROM main', con, parse_dates=['date'])

                df = pd.DataFrame(sql_query, columns=['sku', 'sku_number', 'marketplace', 'date', 'type', 'comment'])

                df['type'] = df['type'].apply(lambda x: lexicon_dict[x])
                df['marketplace'] = df['marketplace'].apply(lambda x: lexicon_dict[x])
                df['date'] = pd.to_datetime(df['date']).dt.date.apply(lambda x: x.strftime('%d/%m/%Y'))

                df.rename(columns={'type': 'Тип проблемы',
                                   'date': 'Дата',
                                   'marketplace': 'Маркетплейс',
                                   'sku_number': 'Артикул',
                                   'comment': 'Комментарий'}, inplace=True)

                result = df.drop(['sku'], axis=1)

                st.dataframe(result, hide_index=True, use_container_width=True)

        if st.session_state['filter_selector'] == 'По дням':
            with sqlite3.connect(db) as con:
                sql_query = pd.read_sql('SELECT * FROM main', con, parse_dates=['date'])

                df = pd.DataFrame(sql_query, columns=['sku', 'sku_number', 'marketplace', 'date', 'type', 'comment'])

                first_date = datetime.date(2022, 12, 13)
                today = datetime.datetime.now()

                df['type'] = df['type'].apply(lambda x: lexicon_dict[x])
                df['marketplace'] = df['marketplace'].apply(lambda x: lexicon_dict[x])
                # df['date'] = pd.to_datetime(df['date']).dt.date.apply(lambda x: x.strftime('%d/%m/%Y'))
                df['date'] = pd.to_datetime(df['date']).dt.date

                df.rename(columns={'type': 'Тип проблемы',
                                   'date': 'Дата',
                                   'marketplace': 'Маркетплейс',
                                   'sku_number': 'Артикул',
                                   'comment': 'Комментарий'}, inplace=True)

                df = df.drop(['sku'], axis=1)
                st.session_state['result_df'] = df

                with st.form("my_form"):
                    st.session_state['day_selector'] = st.date_input('Выбор дней:',
                                                                     (first_date, today),
                                                                     min_value=first_date,
                                                                     format="DD.MM.YYYY")
                    submitted = st.form_submit_button("Применить фильтр")
                    if submitted:
                        x = st.session_state['day_selector'][0]
                        y = st.session_state['day_selector'][1]

                        df = df.loc[(df['Дата'] >= x) & (df['Дата'] < y)]
                        st.session_state['result_df'] = df

                st.dataframe(st.session_state['result_df'], hide_index=True, use_container_width=True)

    elif st.session_state['stats_selector'] == 'Статистика по типу проблемы по месяцам':
        st.header('Статистика по типу проблемы по месяцам')
        with sqlite3.connect(db) as con:
            sql_query = pd.read_sql('SELECT * FROM main', con, parse_dates=['date'])

            df = pd.DataFrame(sql_query, columns=['sku', 'sku_number', 'marketplace', 'date', 'type', 'comment'])
            df.rename(columns={'type': 'type_of_problem'}, inplace=True)

            defect_df = df.query('type_of_problem == "defect"').groupby(
                by=[pd.Grouper(key='date', freq='M')]).size().reset_index()

            bad_package_df = df.query('type_of_problem == "bad_package"').groupby(
                by=[pd.Grouper(key='date', freq='M')]).size().reset_index()

            agg_df = defect_df.merge(bad_package_df, on='date')
            agg_df.rename(columns={'date': 'Месяц',
                                   '0_x': 'Проблемы с товаром',
                                   '0_y': 'Проблемы со сборкой'},
                          inplace=True)

            agg_df['Месяц'] = agg_df['Месяц'].apply(lambda x: x.strftime('%B-%Y'))
            agg_df['Месяц'] = agg_df['Месяц'].apply(lambda x: month_dict[x[:-4]]+' '+x[-4:])

            st.dataframe(agg_df, use_container_width=True, hide_index=True)

    elif st.session_state['stats_selector'] == 'Общая статистика по артикулу':
        st.header('Общая статистика по артикулу')
        with sqlite3.connect(db) as con:
            sql_query = pd.read_sql('SELECT * FROM main', con, parse_dates=['date'])
            df = pd.DataFrame(sql_query, columns=['sku', 'sku_number', 'marketplace', 'date', 'type', 'comment'])
            df.rename(columns={'type': 'type_of_problem'}, inplace=True)

            defect_df = df.query('type_of_problem == "defect"').groupby(
                by=['sku_number']).size().reset_index()

            bad_package_df = df.query('type_of_problem == "bad_package"').groupby(
                by=['sku_number']).size().reset_index()

            agg_df = defect_df.merge(bad_package_df, on='sku_number')
            agg_df.rename(columns={'sku_number': 'Артикул',
                                   '0_x': 'Проблемы с товаром',
                                   '0_y': 'Проблемы со сборкой'},
                          inplace=True)

            st.dataframe(agg_df, use_container_width=True, hide_index=True)

    elif st.session_state['stats_selector'] == 'Статистика по маркетам':
        st.header('Статистика по маркетам')
        with sqlite3.connect(db) as con:
            sql_query = pd.read_sql('SELECT * FROM main', con, parse_dates=['date'])
            df = pd.DataFrame(sql_query, columns=['sku', 'sku_number', 'marketplace', 'date', 'type', 'comment'])
            df.rename(columns={'type': 'type_of_problem'}, inplace=True)

            defect_df = df.query('type_of_problem == "defect"').groupby(
                by=['marketplace']).size().reset_index()

            bad_package_df = df.query('type_of_problem == "bad_package"').groupby(
                by=['marketplace']).size().reset_index()

            agg_df = defect_df.merge(bad_package_df, on='marketplace')
            agg_df.rename(columns={'marketplace': 'Маркетплейс',
                                   '0_x': 'Проблемы с товаром',
                                   '0_y': 'Проблемы со сборкой'},
                          inplace=True)

            st.dataframe(agg_df, use_container_width=True, hide_index=True)

    elif st.session_state['stats_selector'] == 'Статистика по группам артикулов':
        st.header('Статистика по группам артикулов')
        with sqlite3.connect(db) as con:
            sql_query = pd.read_sql('SELECT * FROM main', con, parse_dates=['date'])
            df = pd.DataFrame(sql_query, columns=['sku', 'sku_number', 'marketplace', 'date', 'type', 'comment'])
            df.rename(columns={'type': 'type_of_problem'}, inplace=True)

            group1 = [x for x in range(100, 200)]
            result = df.query('sku_number == @group1').groupby(by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                {'sku_number': 'count'}).reset_index()

            st.subheader('Группа артикулов 100-199')
            st.dataframe(result, use_container_width=True, hide_index=True)

            group2 = [x for x in range(200, 300)]
            result = df.query('sku_number == @group2').groupby(by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                {'sku_number': 'count'}).reset_index()

            st.subheader('Группа артикулов 200-299')
            st.dataframe(result, use_container_width=True, hide_index=True)

            group3 = [x for x in range(300, 400)]
            result = df.query('sku_number == @group3').groupby(by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                {'sku_number': 'count'}).reset_index()

            st.subheader('Группа артикулов 300-399')
            st.dataframe(result, use_container_width=True, hide_index=True)

            group4 = [400, 401, 402, 403, 404, 468, 473]
            result = df.query('sku_number == @group4').groupby(by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                {'sku_number': 'count'}).reset_index()

            st.subheader('Группа артикулов 400-499')
            st.dataframe(result, use_container_width=True, hide_index=True)

            group5 = [413, 416, 418, 422, 423, 427, 446, 447, 448, 449, 450, 451, 452, 454, 455, 457, 460, 464]
            result = df.query('sku_number == @group5').groupby(by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                {'sku_number': 'count'}).reset_index()

            st.subheader('Группа артикулов ГЛТ 411-513')
            st.dataframe(result, use_container_width=True, hide_index=True)

            group6 = [x for x in range(500, 600)]
            result = df.query('sku_number == @group6').groupby(by=[pd.Grouper(key='date', freq='M'), 'marketplace']).agg(
                {'sku_number': 'count'}).reset_index()

            st.subheader('Группа артикулов ГЛТ 500-600')
            st.dataframe(result, use_container_width=True, hide_index=True)

    st.divider()

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