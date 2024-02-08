import sqlite3

import pandas as pd
import streamlit as st

from bitrix24_funcs import b, update_dimensions
from bitrix2sql import refresh_db


def render_dim():
    bitcol1, bitcol2 = st.columns([2, 3])

    with bitcol1:
        with st.form('refresh_form'):
            refresh_button = st.form_submit_button('Обновить буфер заказов', use_container_width=True)

            if refresh_button:
                refresh_db()
                st.toast('Список заказов обновлен')

    column_cfg = {
        'order_id': st.column_config.TextColumn(
            'Bitrix ID'
        ),
        'order_number_1c': st.column_config.TextColumn(
            'Номер заказа 1С'
        ),
        'status': st.column_config.TextColumn(
            'Статус в Битрикс'
        ),
        'link': st.column_config.LinkColumn(
            'Bitrix ID',
            display_text="https://greenea\.bitrix24\.ru/crm/deal/details/(.*?)/",
            width='small'
        )
    }

    with sqlite3.connect('greenea_issues.db') as db:
        order_dataframe = pd.read_sql('SELECT * from bitrix_buffer', db)
    with bitcol1:
        order_dataframe['link'] = order_dataframe['order_id'].apply(lambda x: f'https://greenea.bitrix24.ru/crm/deal'
                                                                              f'/details/{x}/')
        temp = order_dataframe[['link', 'order_number_1c', 'status', 'dims']]
        temp['Введены габариты'] = temp['dims'].apply(lambda x: True if len(x) > 0 else False)
        temp = temp[['link', 'order_number_1c', 'status', 'Введены габариты']]

        st.dataframe(temp,
                     use_container_width=True,
                     hide_index=True,
                     column_config=column_cfg)
        order_options = list(order_dataframe['order_number_1c'])
        order_options.sort()
    with bitcol2:
        order_selector = st.selectbox('Выбор заказа',
                                      options=order_options)

        order_id = order_dataframe.loc[order_dataframe['order_number_1c'] == order_selector]['order_id']
        order_id = str(order_id.iloc[0])
        leads = b.callMethod('crm.deal.get', ID=order_id)

        dimensions = leads['UF_CRM_1704976176405']

        if dimensions:
            st.subheader('Габариты')
            dimensions = dimensions.split(';')
            for string in dimensions:
                st.write(f'{string}')
        else:
            st.write('Габариты еще не введены.')

        if 'qny_of_box' not in st.session_state:
            st.session_state['qny_of_box'] = 0

        if 'box_min' not in st.session_state:
            st.session_state['box_min'] = None

        if 'result_dict' not in st.session_state:
            st.session_state['result_dict'] = {}


        init_box = st.button('Добавить место',
                             use_container_width=True)
        delete_box = st.button('Удалить место',
                               use_container_width=True)

        if init_box:
            st.session_state['qny_of_box'] += 1

        if delete_box:
            if st.session_state['qny_of_box'] > 0:
                st.session_state['qny_of_box'] -= 1
                idx = st.session_state['qny_of_box'] + 1
                del st.session_state['result_dict'][idx]
            else:
                pass

        dims_col1, dims_col2, dims_col3 = st.columns([1, 2, 1])
        for i in range(1, st.session_state['qny_of_box'] + 1):
            with dims_col1:
                qny = st.number_input('Количество',
                                      key=f'qny_{i}',
                                      min_value=1,
                                      step=1)
            with dims_col2:
                dims = st.text_input('Габариты',
                                     key=f'dims_{i}',
                                     placeholder='см х см х см')

            with dims_col3:
                weight = st.number_input('Вес',
                                         key=f'weight_{i}',
                                         min_value=0.0,
                                         value=0.0,
                                         step=0.5)

            st.session_state['result_dict'][i] = [qny, dims, weight]

        if st.session_state['qny_of_box'] > 0:
            update_flag = False
            delete_flag = False
        else:
            update_flag = True
            delete_flag = True

        update_dims = st.button('Обновить информацию о габаритах',
                                use_container_width=True,
                                disabled=update_flag)

        if update_dims:
            result = ""
            temp_dict = st.session_state['result_dict']
            total = 0
            for key, value in temp_dict.items():
                result += f"{value[1]}, вес {value[2]} кг х {value[0]}шт.;"
                total += int(value[0])

            st.subheader(f'Всего количество мест: {total}')
            st.session_state['qny_of_box'] = 0
            st.session_state['result_dict'] = {}
            update_dimensions(int(order_id), result)
