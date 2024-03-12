from datetime import datetime
import datetime
import numpy as np

from dateutil import relativedelta

import streamlit as st

import lexicon
from config import db
from dashboard_functions import render_default_dataframe, change_worker, change_date, render_period_pivot, get_years, \
    get_months
import pandas as pd
import altair as alt

from graph_render import draw_b2b

b2b_column_list = ['type',
                   'bitrix_id',
                   'sku',
                   'sku_number',
                   'date',
                   'worker',
                   'comment',
                   ]


def render_b2b_tab():
    df = render_default_dataframe(db, 'main', b2b_column_list, b2b=True)

    df['type'] = df['type'].apply(lambda x: lexicon.lexicon_dict[x])
    df['sku'] = df['sku'].apply(lambda x: lexicon.lexicon_dict[x])
    df['sku_number'] = df['sku_number'].apply(lambda x: str(x))

    df['Артикул'] = df['sku'] + df['sku_number']
    df = df.drop(['sku', 'sku_number'], axis=1)

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    df = df.rename(columns={'type': 'Тип проблемы',
                            'bitrix_id': 'Номер заказа',
                            'date': 'Дата',
                            'worker': 'Ответственный',
                            'comment': 'Комментарий'})

    b2b_editor_cfg = {
        'Тип проблемы': st.column_config.SelectboxColumn(
            'Тип проблемы',
            width='medium',
            options=['Проблема со сборкой',
                     'Проблема с товаром',
                     'Проблема с доставкой'],
            required=True,
        ),
        'Дата': st.column_config.DateColumn(
            'Дата'
        ),
        'Ответственный': st.column_config.SelectboxColumn(
            'Ответственный',
            width='medium',
            options=['Сборщик 1',
                     'Сборщик 2',
                     'Нет'],
            required=True
        ),
        'Номер заказа': st.column_config.TextColumn(
            'Номер заказа',
            width='small'
        )
    }

    b2b_col1, b2b_col2, b2b_col3 = st.columns([1, 1, 1])

    with b2b_col1:
        worker_selector = st.selectbox('Ответственный',
                                       options=['Все',
                                                'Сборщик 1',
                                                'Сборщик 2'])

    with b2b_col2:
        list_of_years = get_years()
        list_of_years.sort(reverse=True)
        st.session_state['b2b_graph_year_selector'] = st.selectbox('Год', options=list_of_years, key='hzb2b')

    with b2b_col3:
        period = 'day'
        day_selector = True
        list_of_month = get_months(st.session_state['b2b_graph_year_selector'], day_selector=day_selector)
        list_of_month.sort(reverse=True)

        list_of_month = list(map(lambda x: lexicon.numerical_month_dict[x], list_of_month))
        st.session_state['b2b_graph_month_selector'] = st.selectbox('Месяц', options=list_of_month, key='b2b_smrndm')

    match worker_selector:
        case 'Все':
            result_df = df
        case 'Сборщик 1':
            result_df = df.query('Ответственный == "Сборщик 1"')
        case 'Сборщик 2':
            result_df = df.query('Ответственный == "Сборщик 2"')
        case _:
            result_df = df


    temp_year = st.session_state['b2b_graph_year_selector']
    temp_month = lexicon.alpha_month_dict[st.session_state['b2b_graph_month_selector']]

    result_df = result_df.query('year == @temp_year')
    result_df = result_df.query('month == @temp_month')

    with st.form('save b2b table'):
        if result_df.shape[0] > 0:
            b2b_editor = st.data_editor(result_df,
                                        use_container_width=True,
                                        hide_index=True,
                                        column_config=b2b_editor_cfg,
                                        column_order=['Тип проблемы',
                                                      'Номер заказа',
                                                      'Дата',
                                                      'Артикул',
                                                      'Ответственный',
                                                      'Комментарий'],
                                        disabled=['Тип проблемы',
                                                  'Номер заказа',
                                                  'Артикул',
                                                  'Комментарий'],
                                        key='b2b_editor'
                                        )
        else:
            st.write('Нет данных за выбранный период')

        save_b2b_table_btn = st.form_submit_button('Сохранить изменения',
                                                   use_container_width=True)

        st.caption('Сохранение изменений в строчках с проблемой с доставкой не предусмотрено.')

        if save_b2b_table_btn:
            edit_b2b_dict = st.session_state["b2b_editor"]['edited_rows']
            for key, value in edit_b2b_dict.items():
                order_id = df['Номер заказа'].iloc[key]
                worker = b2b_editor['Ответственный'].iloc[key]
                date = b2b_editor['Дата'].iloc[key]
                change_worker(order_id, worker)
                change_date(order_id, date)
            st.toast('Данные обновлены')

    if temp_month < 10:
        start_date = f'{temp_year}-0{temp_month}-01'

    else:
        start_date = f'{temp_year}-{temp_month}-01'


    if start_date[5:7] == '12':
        end_date = f'{temp_year+1}-01-01'
    else:
        end_date = f'{temp_year}-{temp_month+1}-01'

    b2b_chart = draw_b2b(start=start_date,
                         end=end_date,
                         period=period,
                         b2b=True)

    st.altair_chart(b2b_chart, use_container_width=True, theme=None)
