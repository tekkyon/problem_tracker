import datetime
import streamlit as st
import pandas as pd

import lexicon
from config import db
from dashboard_functions import render_default_dataframe, render_sku_table, get_months, color_marketplace, get_years
from table_funcs import render_common_table, render_sku_groups_table

first_date = datetime.date(2022, 12, 13)
today = datetime.datetime.now()


def render_tables_tab():
    col1, col2 = st.columns([1, 4])

    with col1:
        st.session_state['stats_selector'] = st.selectbox(
            'Какой тип статистики интересует?',
            options=['Общая таблица',
                     'По типу проблемы',
                     'По артикулу',
                     'По группам артикулов'],
            label_visibility='collapsed'
        )

        if st.session_state['stats_selector'] == 'Общая таблица':
            st.session_state['result_df'] = None
            st.session_state['common_tab_selector'] = st.selectbox('Выбор дней или месяцев',
                                                                   options=['По дням',
                                                                            'По месяцам'],
                                                                   label_visibility='collapsed')

            if st.session_state['common_tab_selector'] == 'По дням':
                with st.form("my_form"):
                    st.session_state['day_selector'] = st.date_input('Выбор дней:',
                                                                     (first_date, today),
                                                                     min_value=first_date,
                                                                     format="DD.MM.YYYY",
                                                                     label_visibility='collapsed')
                    submitted = st.form_submit_button("Применить фильтр",
                                                      use_container_width=True)
                    if submitted:
                        st.session_state['day_1'] = st.session_state['day_selector'][0]
                        st.session_state['day_2'] = st.session_state['day_selector'][1]

                st.session_state['result_df'] = render_common_table()

                with col2:
                    m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
                    with m_col1:
                        st.metric(label="Общее количество проблем",
                                  value=st.session_state['total_problems'])
                    with m_col2:
                        st.metric(label="Количество за выбранный период",
                                  value=st.session_state['period_problems'])

            else:
                df = render_default_dataframe(db, 'main', lexicon.columns_list)
                first_year = df['date'].min().year
                this_year = df['date'].max().year
                year_list = list(range(first_year, this_year + 1))
                year_list.sort(reverse=True)

                y_m_dct = {}
                for year in year_list:
                    lst = get_months(year, shift=False)
                    y_m_dct[year] = lst

                pcol1, pcol2 = st.columns([1, 1])
                with pcol1:
                    st.session_state['year_1'] = st.selectbox('Год',
                                                              options=y_m_dct.keys(),
                                                              label_visibility='collapsed')

                    month_list_idx = len(y_m_dct[st.session_state['year_1']]) - 1

                with pcol2:
                    st.session_state['month_1'] = st.selectbox('Месяц',
                                                               options=y_m_dct[st.session_state['year_1']],
                                                               label_visibility='collapsed',
                                                               index=month_list_idx)

                with st.form("my_form2"):
                    submitted = st.form_submit_button("Применить фильтр",
                                                      use_container_width=True)
                    if submitted:
                        df = df[
                            (df['date'].dt.year == st.session_state['year_1']) & (
                                    df['date'].dt.month == st.session_state[
                                'month_1'])]

                        df['type'] = df['type'].apply(lambda x: lexicon.lexicon_dict[x])
                        df['marketplace'] = df['marketplace'].apply(lambda x: lexicon.lexicon_dict[x])
                        df.rename(columns={'type': 'Тип проблемы',
                                           'date': 'Дата',
                                           'marketplace': 'Маркетплейс',
                                           'sku_number': 'Артикул',
                                           'comment': 'Комментарий'}, inplace=True)
                        df['Дата'] = pd.to_datetime(df['Дата']).dt.date
                        df = df.sort_values(by=['Дата'], ascending=True)
                        with col2:
                            st.session_state['result_df'] = df
                            st.session_state['period_problems'] = df.shape[0]

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
            df = render_default_dataframe(db, 'main', lexicon.columns_list)
            df = df.rename(columns={'type': 'type_of_problem'})

            with col2:
                render_sku_groups_table(lexicon.sku_groups, df)

        elif st.session_state['stats_selector'] == 'По типу проблемы':
            st.session_state['result_df'] = None
            st.session_state['period_selector'] = st.selectbox(
                'За какой период?',
                options=lexicon.filter_options,
                label_visibility='collapsed'
            )

            with col1:
                st.session_state['delta_option'] = st.radio(label='type of delta',
                                                            options=['ABS', '%'],
                                                            label_visibility='collapsed',
                                                            horizontal=True)

            if st.session_state['period_selector'] == 'За все время':
                df = render_default_dataframe(db, 'main', lexicon.columns_list)
                df.rename(columns={'type': 'type_of_problem'}, inplace=True)
                df['month&year'] = df['date'].dt.to_period('M')
                df['year'] = df['date'].dt.year
                list_of_markets = list(df['marketplace'].unique())

                with col2:
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

                        m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
                        with m_col1:
                            if st.session_state['total_month_before'] is None:
                                if st.session_state['delta_option'] == 'ABS':
                                    delta = 0
                                else:
                                    delta = '0%'

                            else:
                                if st.session_state['delta_option'] == 'ABS':
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
                                if st.session_state['delta_option'] == 'ABS':
                                    delta = 0
                                else:
                                    delta = '0%'

                            else:
                                if st.session_state['delta_option'] == 'ABS':
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
                                if st.session_state['delta_option'] == 'ABS':
                                    delta = 0
                                else:
                                    delta = '0%'

                            else:
                                if st.session_state['delta_option'] == 'ABS':
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

            if st.session_state['period_selector'] == 'По месяцам':
                with col1:
                    list_of_years = get_years()
                    st.session_state['table_year_selector'] = st.selectbox(label='filter year',
                                                                           options=list_of_years,
                                                                           label_visibility='collapsed',
                                                                           index=len(list_of_years) - 1)

                    list_of_month = get_months(st.session_state['table_year_selector'],
                                               shift=False)

                    list_of_month = list(map(lambda x: lexicon.numerical_month_dict[x], list_of_month))

                    st.session_state['table_month_selector'] = st.selectbox(label='filter month',
                                                                            options=list_of_month,
                                                                            label_visibility='collapsed',
                                                                            index=len(list_of_month) - 1)
                    st.session_state['table_month_selector'] = [i for i in lexicon.numerical_month_dict if
                                                                lexicon.numerical_month_dict[i] == st.session_state[
                                                                    'table_month_selector']][0]

                    month = st.session_state['table_month_selector']
                    year = st.session_state['table_year_selector']

                if month < 10:
                    selected_date_string = f'{year}-0{month}'
                else:
                    selected_date_string = f'{year}-{month}'

                df = render_default_dataframe(db, 'main', lexicon.columns_list)
                df.rename(columns={'type': 'type_of_problem'}, inplace=True)

                df['month&year'] = df['date'].dt.to_period('M')
                df['year'] = df['date'].dt.year

                list_of_markets = list(df['marketplace'].unique())

                with col2:
                    for date in df['month&year'].unique():
                        flag = str(date) == selected_date_string
                        month_df = pd.DataFrame(columns=['Маркетплейс', 'Проблема с товаром', 'Проблема со сборкой'])

                        if flag:
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

                        if st.session_state['total_month_before'] is None:
                            if st.session_state['delta_option'] == 'ABS':
                                total_delta = 0
                            else:
                                total_delta = '0%'

                        else:
                            if st.session_state['delta_option'] == 'ABS':
                                total_delta = int(total_this_month - st.session_state['total_month_before'])
                            else:
                                try:
                                    total_delta = round(float(
                                        (total_this_month - st.session_state['total_month_before']) /
                                        st.session_state[
                                            'total_month_before'] * 100), 2)
                                    total_delta = f'{total_delta}%'
                                except:
                                    total_delta = '0%'

                        if st.session_state['defect_month_before'] is None:
                            if st.session_state['delta_option'] == 'ABS':
                                defect_delta = 0
                            else:
                                defect_delta = '0%'

                        else:
                            if st.session_state['delta_option'] == 'ABS':
                                defect_delta = int(defect_this_month - st.session_state['defect_month_before'])
                            else:
                                try:
                                    defect_delta = round(float(
                                        (defect_this_month - st.session_state['defect_month_before']) /
                                        st.session_state['defect_month_before'] * 100), 2)
                                    defect_delta = f'{defect_delta}%'
                                except:
                                    defect_delta = '0%'

                        if st.session_state['package_month_before'] is None:
                            if st.session_state['delta_option'] == 'ABS':
                                package_delta = 0
                            else:
                                package_delta = '0%'

                        else:
                            if st.session_state['delta_option'] == 'ABS':
                                package_delta = int(package_this_month - st.session_state['package_month_before'])
                            else:
                                try:
                                    package_delta = round(float(
                                        (package_this_month - st.session_state['package_month_before']) /
                                        st.session_state['package_month_before'] * 100), 2)
                                    package_delta = f'{package_delta}%'
                                except:
                                    package_delta = '0%'
                        st.session_state['total_month_before'] = total_this_month
                        st.session_state['defect_month_before'] = defect_this_month
                        st.session_state['package_month_before'] = package_this_month

                        if flag:
                            m_col1, m_col2, m_col3 = st.columns([2, 2, 2])
                            with m_col1:
                                st.metric('Количество проблем за период',
                                          total_this_month,
                                          total_delta,
                                          delta_color='inverse')

                            with m_col2:
                                st.metric('Проблемы с товаром',
                                          defect_this_month,
                                          defect_delta,
                                          delta_color='inverse')

                            with m_col3:
                                st.metric('Проблемы со сборкой',
                                          package_this_month,
                                          package_delta,
                                          delta_color='inverse')
                            st.table(month_df.set_index('Маркетплейс'))
                            st.session_state['total_month_before'] = None
                            st.session_state['defect_month_before'] = None
                            st.session_state['package_month_before'] = None
                            break

                st.session_state['defect_month_before'] = None

                st.session_state['package_month_before'] = None

                st.session_state['total_month_before'] = None

            if st.session_state['period_selector'] == 'За год':
                list_of_years = get_years()
                st.session_state['table_year_selector'] = st.selectbox(label='filter year',
                                                                       options=list_of_years,
                                                                       label_visibility='collapsed',
                                                                       index=len(list_of_years) - 1)

                year_selected = st.session_state['table_year_selector']

                list_of_month = get_months(year_selected,
                                           shift=False)

                df = render_default_dataframe(db, 'main', lexicon.columns_list)
                list_of_markets = list(df['marketplace'].unique())
                df.rename(columns={'type': 'type_of_problem'}, inplace=True)

                df['year'] = df['date'].dt.year
                df['month'] = df['date'].dt.month

                df = df.query('year == @year_selected')

                with col2:
                    for month in list_of_month:
                        st.subheader(lexicon.numerical_month_dict[month])
                        month_df = df.query('month == @month')

                        if year_selected == '2022':
                            st.session_state['defect_month_before'] = None
                            st.session_state['package_month_before'] = None
                            st.session_state['total_month_before'] = None
                        else:
                            last_y_m_df = render_default_dataframe(db,
                                                                   'main',
                                                                   lexicon.columns_list)
                            last_y_m_df['year'] = last_y_m_df['date'].dt.year
                            last_y_m_df['month'] = last_y_m_df['date'].dt.month
                            temp_y = year_selected - 1
                            last_y_m_df = last_y_m_df.query('year == @temp_y & month == 12')
                            last_y_m_df.rename(columns={'type': 'type_of_problem'}, inplace=True)
                            st.session_state['defect_month_before'] = \
                                last_y_m_df.query('type_of_problem == "defect"').shape[0]
                            st.session_state['package_month_before'] = \
                                last_y_m_df.query('type_of_problem == "bad_package"').shape[0]
                            st.session_state['total_month_before'] = st.session_state['defect_month_before'] + \
                                                                     st.session_state['package_month_before']

                        market_month_df = pd.DataFrame(columns=['Маркетплейс',
                                                                'Проблема с товаром',
                                                                'Проблема со сборкой'])

                        for market in list_of_markets:
                            qny_defect = \
                                month_df.query(f'type_of_problem == "defect" & marketplace == "{market}"').shape[0]
                            bad_package = \
                                month_df.query(f'type_of_problem == "bad_package" & marketplace == "{market}"').shape[0]
                            data = {'Маркетплейс': lexicon.lexicon_dict[market],
                                    'Проблема с товаром': qny_defect,
                                    'Проблема со сборкой': bad_package}
                            market_month_df.loc[len(market_month_df)] = data

                        defect_this_month = market_month_df['Проблема с товаром'].sum()
                        package_this_month = market_month_df['Проблема со сборкой'].sum()
                        total_this_month = defect_this_month + package_this_month

                        m_col1, m_col2, m_col3 = st.columns([2, 2, 2])

                        with m_col1:
                            if st.session_state['total_month_before'] is None:
                                if st.session_state['delta_option'] == 'ABS':
                                    delta = 0
                                else:
                                    delta = '0%'

                            else:
                                if st.session_state['delta_option'] == 'ABS':
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
                                if st.session_state['delta_option'] == 'ABS':
                                    delta = 0
                                else:
                                    delta = '0%'

                            else:
                                if st.session_state['delta_option'] == 'ABS':
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
                                if st.session_state['delta_option'] == 'ABS':
                                    delta = 0
                                else:
                                    delta = '0%'

                            else:
                                if st.session_state['delta_option'] == 'ABS':
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

                        st.table(market_month_df.set_index('Маркетплейс'))

                st.session_state['defect_month_before'] = None

                st.session_state['package_month_before'] = None

                st.session_state['total_month_before'] = None

        elif st.session_state['stats_selector'] == 'По артикулу':
            st.session_state['result_df'] = None
            df = render_default_dataframe(db, 'main', lexicon.columns_list)
            df.rename(columns={'type': 'type_of_problem'}, inplace=True)

            with col1:
                st.session_state['sku_table_selector'] = st.selectbox('Сводная таблица',
                                                                      options=[
                                                                          'Сводная таблица',
                                                                          'Детализация'
                                                                      ],
                                                                      label_visibility='collapsed')

                if st.session_state['sku_table_selector'] == 'Сводная таблица':

                    st.session_state['sku_radio_selector'] = st.radio('Отобразить:',
                                                                      options=['По типу проблемы',
                                                                               'По маркетплейсам'])
                    if st.session_state['sku_radio_selector'] == 'По типу проблемы':
                        defect_df = df.query('type_of_problem == "defect"').groupby(
                            by=['sku_number']).size().reset_index()

                        bad_package_df = df.query('type_of_problem == "bad_package"').groupby(
                            by=['sku_number']).size().reset_index()

                        agg_df = defect_df.merge(bad_package_df, on='sku_number', how='outer')
                        agg_df.rename(columns={'sku_number': 'Артикул',
                                               '0_x': 'Проблемы с товаром',
                                               '0_y': 'Проблемы со сборкой'},
                                      inplace=True)
                        agg_df = agg_df.set_index(['Артикул'])
                        agg_df = agg_df.fillna(0)
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

                elif st.session_state['sku_table_selector'] == 'Детализация':
                    with col1:

                        sku_selector = st.selectbox('Выбор артикула',
                                                    options=df['sku_number'].unique(),
                                                    placeholder='Выберите артикул',
                                                    label_visibility='collapsed')

                        df = df.query('sku_number == @sku_selector')[['marketplace',
                                                                      'date',
                                                                      'type_of_problem',
                                                                      'comment']]

                        df['marketplace'] = df['marketplace'].apply(lambda x: lexicon.lexicon_dict[x])
                        df['type_of_problem'] = df['type_of_problem'].apply(lambda x: lexicon.lexicon_dict[x])

                        df = df.rename(columns={'marketplace': 'Маркетплейс',
                                                'date': 'Дата',
                                                'type_of_problem': 'Тип проблемы',
                                                'comment': 'Комментарий'})

                        st.session_state['result_df'] = df

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
