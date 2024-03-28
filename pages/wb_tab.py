import streamlit as st
import pandas as pd
import math

def render_wb_tab():
    initial_table_wb = st.file_uploader('Таблица из ЛК маркетплейса', type='xlsx', key='initial_table_wb')

    fee_column = st.columns([1, 1, 1])

    with fee_column[0]:
        delivery_fee_1 = st.number_input(label='доставка 1',
                                         value=60)
    with fee_column[1]:
        delivery_fee_2 = st.number_input(label='доставка 2',
                                         value=14.17)
    with fee_column[2]:
        wb_margin = st.number_input(label='маржа %',
                                    value=30)
    if initial_table_wb is not None:
        st.session_state['initial_wb'] = pd.read_excel(initial_table_wb)
        st.session_state['cost_wb'] = pd.read_pickle('pages/wb_selfcost.pkl')

        ct_wb = st.session_state['initial_wb'].copy()
        ct_wb = ct_wb.merge(st.session_state['cost_wb'], on='Артикул поставщика')

        st.divider()
        try:
            ct_wb['Разница в скидках'] = ct_wb['Загружаемая скидка для участия в акции'] - \
                                         ct_wb['Текущая скидка на сайте, %']

            ct_wb['Текущая цена на сайте'] = ct_wb['Текущая розничная цена'] - (
                    ct_wb['Текущая розничная цена'] * ct_wb['Текущая скидка на сайте, %'] / 100)

            ct_wb['Разница в ценах'] = ct_wb['Текущая цена на сайте'] - ct_wb[
                'Плановая цена для акции']

            ct_wb['Отклонение текущей от РРЦ'] = ct_wb['Текущая цена на сайте'] - ct_wb['РРЦ']

            ct_wb['Отклонение плановой от РРЦ'] = ct_wb['Плановая цена для акции'] - ct_wb[
                'РРЦ']

            ct_wb['Разница тек.откл. от план.откл.'] = ct_wb['Отклонение текущей от РРЦ'] - \
                                                       ct_wb[
                                                           'Отклонение плановой от РРЦ']

            ct_wb['Комиссия (участие)'] = ct_wb['Плановая цена для акции'] * ct_wb[
                'Себестоимость'] / 100

            ct_wb['Категория объема/л'] = math.ceil(ct_wb['Высота, мм'] * ct_wb['Ширина, мм'] * ct_wb[
                'Глубина, мм'] / 1000000)

            ct_wb['Доставка'] = delivery_fee_1 + delivery_fee_2 * (ct_wb['Категория объема/л'] - 1)

            ct_wb['Плановая цена минус все услуги'] = ct_wb['Плановая цена для акции'] - ct_wb[
                'Комиссия (участие)'] - ct_wb['Доставка']

            ct_wb['Результат (участие)'] = ct_wb['Плановая цена минус все услуги'] - ct_wb[
                'Себестоимость']

            ct_wb['Отклонение от РРЦ'] = ct_wb['РРЦ'] - ct_wb['Результат (участие)'] - \
                                         ct_wb['Себестоимость'] - ct_wb['Комиссия (участие)'] - \
                                         ct_wb['Доставка']

            ct_wb['Отклонение от РРЦ (%)'] = ct_wb['Отклонение от РРЦ'] / 0.01 / ct_wb['РРЦ']

            ct_wb['Маржа (участие)%'] = ct_wb['Результат (участие)'] * 100 / ct_wb[
                'Плановая цена для акции']

            ct_wb['Проходит'] = ct_wb['Маржа (участие)%'] >= wb_margin

            try:
                ct_wb['Себестоимость'] = ct_wb['Себестоимость'].map(lambda x: float(x.replace(',', '.')))
            except AttributeError:
                pass

            ct_wb['Комиссия (участие)'] = ct_wb['Плановая цена для акции'] * ct_wb[
                'Себестоимость'] / 100

            st.dataframe(ct_wb,
                         use_container_width=True,
                         hide_index=True
                         )

        except Exception as e:
            st.write(e)