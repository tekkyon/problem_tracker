import asyncio
import sqlite3

import time

import pandas as pd
import streamlit as st

from fastbitrix_funcs import get_deals
from bitrix24_funcs import update_dimensions_v

from collections import Counter

st.set_page_config(page_title='Габариты',
                   layout='wide',
                   initial_sidebar_state='collapsed',
                   page_icon=':package:')

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)


if 'result_buffer_df' not in st.session_state:
    st.session_state['result_buffer_df'] = None

if 'old_number' not in st.session_state:
    st.session_state['old_number'] = None

if 'new_number' not in st.session_state:
    st.session_state['new_number'] = None


def render_dim():
    bitcol1, bitcol2 = st.columns([1, 10])

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
            'Габариты',
            width='small'
        )
    }
    with bitcol1:
        if 'deals got' not in st.session_state:
            st.session_state['deals got'] = False

        if 'deals_id' not in st.session_state:
            st.session_state['deals_id'] = None

        if 'order_dims_to_send' not in st.session_state:
            st.session_state['order_dims_to_send'] = ''

        if not st.session_state['deals got']:
            st.session_state['deals_id'] = asyncio.run(get_deals())
            st.session_state['deals got'] = True

        order_df = pd.DataFrame.from_dict(st.session_state['deals_id'], orient='index').reset_index()
        order_df['Bitrix ID'] = order_df['ID Заказа'].apply(
            lambda order: f'https://greenea.bitrix24.ru/crm/deal'
                          f'/details/{order}/')
        order_df['Введены габариты'] = order_df['Габариты'].apply(lambda x: True if x is not None else False)
        result_df = order_df.drop(['Габариты', 'ID Заказа'], axis=1)
        # st.dataframe(result_df, use_container_width=True, hide_index=True, column_config=column_cfg)

        def clear_dims():
            st.session_state['order_dims_to_send'] = ''

        order_selector_list = list(result_df['index'])
        order_selector_list.sort()

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
                                      options=order_selector_list,
                                      on_change=refresh_dims,
                                      placeholder='Выберите заказ')

        order_id = order_df.loc[order_df['index'] == order_selector]['Bitrix ID'].iloc[0].split('/')[6]
        dims_from_df = order_df.loc[order_df['index'] == order_selector]['Габариты']
        # st.write(dims_from_df.iloc[0])

        # leads = b.callMethod('crm.deal.get', ID=order_id)
        dimensions = dims_from_df.iloc[0]
        # dimensions = leads['UF_CRM_1704976176405']
        # st.write(dimensions)

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

        # temp_worker_df = get_list_of_workers()
        # temp_worker_df['ИмяФамилия'] = temp_worker_df['lastname'] + ' ' + temp_worker_df['firstname']
        # temp_worker_df = temp_worker_df[['ИмяФамилия', 'worker_id']]
        # temp_worker_df = temp_worker_df.set_index('ИмяФамилия')
        # temp_worker_dict = temp_worker_df.to_dict()
        #
        # temp_worker_dict = temp_worker_dict['worker_id']
        # executor_selector = st.selectbox('Сборщик',
        #                                  options=list(temp_worker_dict.keys()))
        #
        # executor_id = temp_worker_dict[executor_selector]

        st.subheader(f'Общее количество: {temp_qny}')
        st.write(f'Общий вес: {temp_weight} кг.')
        st.write(f'Общий объем: {temp_volume / 1000000} м³.')

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

            temp_volume = f'{round(temp_volume / 1000000, 2)} м³.'
            temp_weight = f'{temp_weight} кг.'
            volume = f'Общий объем: {temp_volume}\nОбщий вес: {temp_weight}\nКоличество мест: {temp_qny}'

            # update_sql_dim(order_id, result, 'placeholder_worker')
            update_dimensions_v(int(order_id), result, volume)
            st.toast('Габариты обновлены')
            time.sleep(1)
            st.rerun()

render_dim()