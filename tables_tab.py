import datetime
import sqlite3

import streamlit as st
import pandas as pd
import lexicon
from config import db
from dashboard_functions import render_default_dataframe, render_sku_table, get_monthes, color_marketplace

first_date = datetime.date(2022, 12, 13)
today = datetime.datetime.now()


def render_tables_tab():
    col1, col2 = st.columns([1, 4])
    with col1:

        st.session_state['stats_selector'] = st.selectbox(
            'Какой тип статистики интересует?',
            options=lexicon.stat_options
        )

        if st.session_state['stats_selector'] not in ['Общая таблица']:
            st.session_state['period_selector'] = st.selectbox(
                'За какой период?',
                options=lexicon.filter_options
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
            st.session_state['common_tab_selector'] = st.selectbox('Выбор дней или месяцев',
                                                                   options=['По дням',
                                                                            'По месяцам'],
                                                                   label_visibility='collapsed')

            if st.session_state['common_tab_selector'] == 'По дням':
                with st.form("my_form"):
                    st.session_state['day_selector'] = st.date_input('Выбор дней:',
                                                                     (first_date, today),
                                                                     min_value=first_date,
                                                                     format="DD.MM.YYYY")
                    submitted = st.form_submit_button("Применить фильтр")
                    if submitted:
                        st.session_state['day_1'] = st.session_state['day_selector'][0]
                        st.session_state['day_2'] = st.session_state['day_selector'][1]

            if st.session_state['common_tab_selector'] == 'По месяцам':
                df = render_default_dataframe(db, 'main', lexicon.columns_list)
                # df['date'] = pd.to_datetime(df['date']).dt.date
                first_year = df['date'].min().year
                this_year = df['date'].max().year
                year_list = list(range(first_year, this_year + 1))
                year_list.sort(reverse=True)

                y_m_dct = {}
                for year in year_list:
                    lst = get_monthes(year)
                    y_m_dct[year] = lst

                pcol1, pcol2 = st.columns([1, 1])
                with pcol1:
                    st.session_state['year_1'] = st.selectbox('Год',
                                                              options=y_m_dct.keys(),
                                                              label_visibility='collapsed')
                with pcol2:

                    st.session_state['month_1'] = st.selectbox('Месяц',
                                                              options=y_m_dct[st.session_state['year_1']],
                                                              label_visibility='collapsed')

                with st.form("my_form2"):
                    submitted = st.form_submit_button("Применить фильтр", use_container_width=True)
                    if submitted:
                        df = df[
                            (df['date'].dt.year == st.session_state['year_1']) & (df['date'].dt.month == st.session_state[
                                'month_1'])]

                        df['type'] = df['type'].apply(lambda x: lexicon.lexicon_dict[x])
                        df['marketplace'] = df['marketplace'].apply(lambda x: lexicon.lexicon_dict[x])
                        df.rename(columns={'type': 'Тип проблемы',
                                           'date': 'Дата',
                                           'marketplace': 'Маркетплейс',
                                           'sku_number': 'Артикул',
                                           'comment': 'Комментарий'}, inplace=True)
                        df['Дата'] = pd.to_datetime(df['Дата']).dt.date
                        with col2:
                            # x = df.style.applymap(color_marketplace, subset='Маркетплейс')
                            # st.session_state['result_df'] = x
                            st.session_state['result_df'] = df

    if st.session_state['stats_selector'] == 'Общая таблица' and st.session_state['common_tab_selector'] == 'По дням':

        df = render_default_dataframe(db, 'main', lexicon.columns_list)
        df['type'] = df['type'].apply(lambda x: lexicon.lexicon_dict[x])
        df['marketplace'] = df['marketplace'].apply(lambda x: lexicon.lexicon_dict[x])
        df.rename(columns={'type': 'Тип проблемы',
                           'date': 'Дата',
                           'marketplace': 'Маркетплейс',
                           'sku_number': 'Артикул',
                           'comment': 'Комментарий'}, inplace=True)
        df['Дата'] = pd.to_datetime(df['Дата']).dt.date
        st.session_state['total_problems'] = df.shape[0]
        df = df.loc[
            (df['Дата'] >= st.session_state['day_1']) & (df['Дата'] <= st.session_state['day_2'])]
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


    elif st.session_state['stats_selector'] == 'По группам артикулов':
        st.session_state['result_df'] = None
        with sqlite3.connect(db) as con:
            sql_query = pd.read_sql('SELECT * FROM main', con, parse_dates=['date'])
            df = pd.DataFrame(sql_query, columns=['sku', 'sku_number', 'marketplace', 'date', 'type', 'comment'])
            df.rename(columns={'type': 'type_of_problem'}, inplace=True)

        with col2:
            st.subheader('Группа артикулов 100-199')
            group = [x for x in range(100, 200)]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов 200-299')
            group = [x for x in range(200, 300)]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов 300-399')
            group = [x for x in range(300, 400)]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов 400-499')
            group = [400, 401, 402, 403, 404, 468, 473]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов ГЛТ 411-513')
            group = [413, 416, 418, 422, 423, 427, 446, 447, 448, 449, 450, 451, 452, 454, 455, 457, 460, 464]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов 500-599')
            group = [x for x in range(500, 600)]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов 600-699')
            group = [606, 610]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов КА')
            group = [660, 'ка-954']
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов 700-799')
            group = [747, 748, 749]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов 800-899')
            group = [832, 849, 850, 855, 865]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов 900-999')
            group = [945, 950, 954, 972, 997, 998]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

            st.subheader('Группа артикулов 1000-1999')
            group = [1000, 1017, 1084, 1127, 1244, 1380, 1384, 1386]
            result = render_sku_table(df, group)
            st.dataframe(result, use_container_width=True)

    elif st.session_state['stats_selector'] == 'По типу проблемы':

        if st.session_state['period_selector'] == 'За все время':
            df = render_default_dataframe(db, 'main', lexicon.columns_list)
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
                new.columns = list(map(lambda x: lexicon.lexicon_dict[x], new.columns))
                new = new.iloc[1:]
                st.dataframe(new, hide_index=False, use_container_width=True)

            st.session_state['result_df'] = None

        if st.session_state['period_selector'] == 'По месяцам':
            with col1:
                st.session_state['delta_option'] = st.radio(label='type of delta',
                                                            options=['Абсолютная разница', 'Разница в процентах'],
                                                            label_visibility='hidden')

            df = render_default_dataframe(db, 'main', lexicon.columns_list)
            df.rename(columns={'type': 'type_of_problem'}, inplace=True)
            df['month&year'] = df['date'].dt.to_period('M')
            df['year'] = df['date'].dt.year
            list_of_markets = list(df['marketplace'].unique())

            with col2:
                list_of_month = []
                for date in df['month&year'].unique():
                    month_df = pd.DataFrame(columns=['Маркетплейс', 'Проблема с товаром', 'Проблема со сборкой'])

                    st.subheader(f'{lexicon.numerical_month_dict[date.month]} {str(date.year)}')

                    temp = df.loc[(df['date'].dt.month == date.month) & (df['date'].dt.year == date.year)]
                    for market in list_of_markets:
                        qny_defect = temp.query(f'type_of_problem == "defect" & marketplace == "{market}"').shape[0]

                        bad_package = \
                            temp.query(f'type_of_problem == "bad_package" & marketplace == "{market}"').shape[0]

                        data = {'Маркетплейс': lexicon.lexicon_dict[market],
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
        df = render_default_dataframe(db, 'main', lexicon.columns_list)
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
                        market_df.rename(columns={'market': lexicon.lexicon_dict[market]}, inplace=True)
                        market_df.set_index('sku_number', inplace=True)

                        if len(result_df) == 0:
                            result_df = market_df
                        else:
                            result_df = pd.merge(result_df, market_df, how='outer', on='sku_number')

                    result_df = result_df.fillna(0)
                    result_df = result_df.reset_index().rename(columns={'sku_number': 'Артикул'})
                    result_df.set_index('Артикул', inplace=True)

                    st.dataframe(result_df, use_container_width=True)
                    st.session_state['result_df'] = None

        if st.session_state['period_selector'] == 'По месяцам':
            st.session_state['result_df'] = None

        if st.session_state['period_selector'] == 'По дням':
            st.session_state['result_df'] = None

    with col2:
        if st.session_state['result_df'] is not None:
            column_config = {
                'Дата': st.column_config.DateColumn('Дата',
                                                    format="DD/MM/YYYY"),
                'Артикул': st.column_config.TextColumn('Артикул')
            }
            st.dataframe(st.session_state['result_df'],
                         hide_index=True,
                         use_container_width=True,
                         column_config=column_config)
            # st.write(st.session_state['result_df'].to_html(index=False), unsafe_allow_html=True)
