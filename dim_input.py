import sqlite3

import time

import pandas as pd
import streamlit as st

from bitrix24_funcs import b, update_dimensions
from bitrix2sql import refresh_db

from collections import Counter

from config import task_db
from db import update_sql_dim, get_list_of_workers, update_status

if 'result_buffer_df' not in st.session_state:
    st.session_state['result_buffer_df'] = None

if 'old_number' not in st.session_state:
    st.session_state['old_number'] = None

if 'new_number' not in st.session_state:
    st.session_state['new_number'] = None


def render_dim():
    bitcol1, bitcol2 = st.columns([2, 3])
    update_list = refresh_db()
    update_status(update_list)
    #             update_status(update_list)
    # with bitcol1:
    #     with st.form('refresh_form'):
    #         refresh_button = st.form_submit_button('Обновить буфер заказов', use_container_width=True)
    #
    #         if refresh_button:
    #             update_list = refresh_db()
    #             update_status(update_list)
    #             st.toast('Список заказов обновлен')

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
        ),
        'Введены габариты': st.column_config.CheckboxColumn(
            'Габариты',
            width='small'
        )
    }

    with sqlite3.connect(task_db) as db:
        order_dataframe = pd.read_sql('SELECT * from orders', db)
        st.session_state['old_number'] = order_dataframe.shape[0]
    with bitcol1:
        order_dataframe['link'] = order_dataframe['order_id'].apply(
            lambda order: f'https://greenea.bitrix24.ru/crm/deal'
                          f'/details/{order}/')
        temp = order_dataframe[['link', 'order_number_1c', 'status', 'dims']]
        temp['Введены габариты'] = temp['dims'].apply(lambda x: False if x=='None' else True)
        st.session_state['result_buffer_df'] = temp[['link', 'order_number_1c', 'status', 'Введены габариты']]

        st.dataframe(st.session_state['result_buffer_df'],
                     use_container_width=True,
                     hide_index=True,
                     column_config=column_cfg,
                     height=555)
        order_options = list(order_dataframe['order_number_1c'])
        order_options.sort()
    with bitcol2:
        if 'qny_of_place' not in st.session_state:
            st.session_state['qny_of_place'] = 0

        if 'result_dict' not in st.session_state:
            st.session_state['result_dict'] = {}

        if 'dims_present' not in st.session_state:
            st.session_state['dims_present'] = None

        if 'dims_loaded' not in st.session_state:
            st.session_state['dims_loaded'] = None

        def refresh_dims():
            st.session_state['qny_of_place'] = 0
            st.session_state['result_dict'] = {}
            st.session_state['dims_loaded'] = True

        order_selector = st.selectbox('Выбор заказа',
                                      options=order_options,
                                      on_change=refresh_dims,
                                      placeholder='Выберите заказ')

        order_id = order_dataframe.loc[order_dataframe['order_number_1c'] == order_selector]['order_id']
        order_id = str(order_id.iloc[0])
        leads = b.callMethod('crm.deal.get', ID=order_id)

        dimensions = leads['UF_CRM_1704976176405']

        if dimensions:
            st.session_state['dims_present'] = True
        else:
            st.session_state['dims_present'] = False
            st.write('Габариты еще не введены.')

        init_box = st.button('Добавить место',
                             use_container_width=True)
        delete_box = st.button('Удалить место',
                               use_container_width=True)

        if init_box:
            st.session_state['qny_of_place'] += 1
            st.session_state['dims_loaded'] = False

        if delete_box:
            if st.session_state['qny_of_place'] > 0:
                st.session_state['dims_loaded'] = False
                st.session_state['qny_of_place'] -= 1
                idx = st.session_state['qny_of_place'] + 1
                del st.session_state['result_dict'][idx]
            else:
                pass

        dims_col1, dims_col2, dims_col3, dims_col4, dims_col5 = st.columns([1, 1, 1, 1, 1])

        if not st.session_state['dims_present']:
            st.session_state['dims_loaded'] = False
            for i in range(1, st.session_state['qny_of_place'] + 1):
                with dims_col1:
                    qny = st.number_input('Количество, шт',
                                          key=f'qny_{i}',
                                          min_value=1,
                                          step=1)
                with dims_col2:
                    dims_x = st.number_input('Ширина, см',
                                             key=f'dims_x_{i}',
                                             min_value=1)
                with dims_col3:
                    dims_y = st.number_input('Длина, см',
                                             key=f'dims_y_{i}',
                                             min_value=1)
                with dims_col4:
                    dims_z = st.number_input('Высота, см',
                                             key=f'dims_z_{i}',
                                             min_value=1)
                with dims_col5:
                    weight = st.number_input('Вес, кг',
                                             key=f'weight_{i}',
                                             min_value=0.0,
                                             value=0.0,
                                             step=0.5)

                st.session_state['result_dict'][i] = [qny, dims_x, dims_y, dims_z, weight]
        else:
            dimensions = dimensions.split()

            comparator = (len(set(dimensions)) == len(dimensions))
            qny_counter = Counter(dimensions)

            counter = 0

            if comparator:
                if st.session_state['dims_loaded']:
                    st.session_state['qny_of_place'] = len(dimensions)

                for idx in range(1, st.session_state['qny_of_place'] + 1):

                    counter += 1

                    if len(dimensions) >= counter:
                        dims, weight = dimensions[idx - 1].split('=')
                        x, y, z = dims.split('*')
                        weight = int(weight) / 1000

                    else:
                        weight = 0.0
                        x, y, z = 1, 1, 1

                    with dims_col1:
                        qny = st.number_input('Количество, шт',
                                              key=f'qny_{idx}',
                                              min_value=1,
                                              step=1)

                    with dims_col2:
                        dims_x = st.number_input('Ширина, см',
                                                 key=f'dims_x_{idx}',
                                                 min_value=1,
                                                 value=int(x))
                    with dims_col3:
                        dims_y = st.number_input('Длина, см',
                                                 key=f'dims_y_{idx}',
                                                 min_value=1,
                                                 value=int(y))
                    with dims_col4:
                        dims_z = st.number_input('Высота, см',
                                                 key=f'dims_z_{idx}',
                                                 min_value=1,
                                                 value=int(z))
                    with dims_col5:
                        weight_input = st.number_input('Вес, кг',
                                                       key=f'weight_{idx}',
                                                       min_value=0.0,
                                                       value=weight,
                                                       step=0.5)
                    idx += 1
                    st.session_state['result_dict'][idx] = [qny, dims_x, dims_y, dims_z, weight_input]

            else:
                dimensions = list(set(dimensions))
                if st.session_state['dims_loaded']:
                    st.session_state['qny_of_place'] = len(dimensions)

                for idx in range(1, st.session_state['qny_of_place'] + 1):

                    counter += 1

                    if len(dimensions) >= counter:
                        qny_input = qny_counter[dimensions[idx - 1]]
                        dims, weight = dimensions[idx - 1].split('=')
                        x, y, z = dims.split('*')
                        weight = int(weight) / 1000

                    else:
                        weight = 0.0
                        x, y, z = 1, 1, 1
                        qny_input = 1

                    with dims_col1:
                        qny = st.number_input('Количество, шт',
                                              key=f'qny_{idx}',
                                              min_value=1,
                                              step=1,
                                              value=qny_input)

                    with dims_col2:
                        dims_x = st.number_input('Ширина, см',
                                                 key=f'dims_x_{idx}',
                                                 min_value=1,
                                                 value=int(x))
                    with dims_col3:
                        dims_y = st.number_input('Длина, см',
                                                 key=f'dims_y_{idx}',
                                                 min_value=1,
                                                 value=int(y))
                    with dims_col4:
                        dims_z = st.number_input('Высота, см',
                                                 key=f'dims_z_{idx}',
                                                 min_value=1,
                                                 value=int(z))
                    with dims_col5:
                        weight_input = st.number_input('Вес, кг',
                                                       key=f'weight_{idx}',
                                                       min_value=0.0,
                                                       value=weight,
                                                       step=0.5)
                    idx += 1
                    st.session_state['result_dict'][idx] = [qny, dims_x, dims_y, dims_z, weight_input]

            st.session_state['dims_loaded'] = False

        if st.session_state['qny_of_place'] > 0:
            update_flag = False
        else:
            update_flag = True

        temp_qny = 0
        temp_weight = 0.0
        temp_volume = 0.0

        if 'qny_1' in st.session_state:
            for i in range(1, st.session_state['qny_of_place'] + 1):
                temp_qny += int(st.session_state[f'qny_{i}'])
                temp_weight += st.session_state[f'weight_{i}'] * int(st.session_state[f'qny_{i}'])
                x = st.session_state[f'dims_x_{i}']
                y = st.session_state[f'dims_y_{i}']
                z = st.session_state[f'dims_z_{i}']
                temp_volume += x * y * z * int(st.session_state[f'qny_{i}'])


        temp_worker_df = get_list_of_workers()
        temp_worker_df['ИмяФамилия'] = temp_worker_df['lastname'] + ' ' + temp_worker_df['firstname']
        temp_worker_df = temp_worker_df[['ИмяФамилия', 'worker_id']]
        temp_worker_df = temp_worker_df.set_index('ИмяФамилия')
        temp_worker_dict = temp_worker_df.to_dict()

        temp_worker_dict = temp_worker_dict['worker_id']
        executor_selector = st.selectbox('Сборщик',
                                         options=list(temp_worker_dict.keys()))

        executor_id = temp_worker_dict[executor_selector]


        st.subheader(f'Общее количество: {temp_qny}')
        st.write(f'Общий вес: {temp_weight} кг.')
        st.write(f'Общий объем: {temp_volume / 1000000} м³.')

        volume_weight_checkbox = st.checkbox('Добавить информацию об общем весе и объеме',
                                             disabled=True)

        update_dims = st.button('Обновить информацию о габаритах',
                                use_container_width=True,
                                disabled=update_flag)

        if update_dims:
            result = ""
            counter = 1
            temp_dict = st.session_state['result_dict']

            for key, value in temp_dict.items():
                for qny in range(1, value[0] + 1):
                    if counter < temp_qny:
                        result += f"{value[1]}*{value[2]}*{value[3]}={int(value[4] * 1000)}\n"
                        counter += 1
                    else:
                        result += f"{value[1]}*{value[2]}*{value[3]}={int(value[4] * 1000)}"
            st.session_state['result_dict'] = {}

            if volume_weight_checkbox:
                temp_volume = f'{temp_volume / 1000000} м³.'
                temp_weight = f'{temp_weight} кг.'
                result = f'{result} общий объем: {temp_volume}; общий вес: {temp_weight}'

            update_sql_dim(order_id, result, executor_id)
            update_dimensions(int(order_id), result)
            st.toast('Габариты обновлены')
            time.sleep(1)
            st.rerun()
