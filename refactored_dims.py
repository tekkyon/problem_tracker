import asyncio

import streamlit as st
import pandas as pd
from collections import Counter

from fastbitrix_funcs import get_deals

column_cfg = {
    'order_id': st.column_config.TextColumn(
        'Bitrix ID'
    ),
    'index': st.column_config.TextColumn(
        'Номер заказа 1С'
    ),
    'status': st.column_config.TextColumn(
        'Статус в Битрикс'
    ),
    'Bitrix ID': st.column_config.LinkColumn(
        'Bitrix ID',
        display_text="https://greenea\.bitrix24\.ru/crm/deal/details/(.*?)/",
        width='small'
    ),
    'Введены габариты': st.column_config.CheckboxColumn(
        'Введены габариты',
        width='small'
    )
}


def render_dim():
    if 'deals got' not in st.session_state:
        st.session_state['deals got'] = False

    if 'deals_id' not in st.session_state:
        st.session_state['deals_id'] = None

    if 'order_dims_to_send' not in st.session_state:
        st.session_state['order_dims_to_send'] = ''

    if not st.session_state['deals got']:
        st.session_state['deals_id'] = asyncio.run(get_deals())
        st.session_state['deals got'] = True
    with st.expander('Таблица заказов'):
        order_df = pd.DataFrame.from_dict(st.session_state['deals_id'], orient='index').reset_index()
        order_df['Bitrix ID'] = order_df['ID Заказа'].apply(
            lambda order: f'https://greenea.bitrix24.ru/crm/deal'
                          f'/details/{order}/')
        order_df['Введены габариты'] = order_df['Габариты'].apply(lambda x: True if x is not None else False)
        result_df = order_df.drop(['Габариты', 'ID Заказа'], axis=1)
        st.dataframe(result_df, use_container_width=True, hide_index=True, column_config=column_cfg)

    def clear_dims():
        st.session_state['order_dims_to_send'] = ''

    order_selector_list = list(result_df['index'])
    order_selector_list.sort()
    order_selector = st.selectbox('Номер заказа',
                                  options=order_selector_list,
                                  on_change=clear_dims)

    dimensions = order_df.query('index == @order_selector')['Габариты'].iloc[0]

    dim_input = st.columns([1, 1, 1, 1, 1])
    with st.form('Ввод габаритов', clear_on_submit=True):
        form_input = st.empty()
        with dim_input[0]:
            form_input.qny = st.number_input(label='Количество')
        with dim_input[1]:
            form_input.w = st.number_input(label='Ширина, см')
        with dim_input[2]:
            form_input.l = st.number_input(label='Длина, см')
        with dim_input[3]:
            form_input.h = st.number_input(label='Высота, см')
        with dim_input[4]:
            form_input.weight = st.number_input(label='Вес, кг')

        save_row = st.form_submit_button('Сохранить место', use_container_width=True)
        if save_row:
            form_input.empty()

    # if dimensions is not None:
    #     dimensions_dict = dict(Counter(dimensions.split()))
    #     dimensions_df = {}
    #     counter = 0
    #     for key, value in dimensions_dict.items():
    #         qny = value
    #         dims, weight_g = key.split('=')
    #         w, l, h = dims.split('*')
    #         dimensions_df[counter] = {'Вес': int(weight_g) / 1000,
    #                                   'Количество': qny,
    #                                   'Ширина': w,
    #                                   'Длина': l,
    #                                   'Высота': h}
    #         counter += 1
    #     dimensions_df = pd.DataFrame.from_dict(dimensions_df, orient='index')
    #     st.dataframe(dimensions_df, hide_index=True)
    # else:
    #     pass


