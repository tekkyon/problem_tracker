import streamlit as st
import pandas as pd
import math

ozon_clm_cfg = {
    'OzonID': st.column_config.TextColumn(
        'OzonID',
        width='small'
    ),
    'Цена до скидки': st.column_config.TextColumn(
        'Цена до скидки'
    )
}

def render_ozon_tab():
    initial_table_ozon = st.file_uploader('Таблица из ЛК маркетплейса', type='xlsx', key='initial_table_ozon')

    ozon_margin = st.number_input(label='маржа %',
                                  value=30,
                                  key='ozon_margin')

    if initial_table_ozon is not None:
        st.session_state['initial_ozon'] = pd.read_excel(initial_table_ozon)
        new_ozon_column_set = set(st.session_state['initial_ozon'].columns)
        ozon_column_set = {'Текущая цена',
                           'Цена до скидки',
                           'Запрашиваемая скидка по акции, %',
                           'Рассчитанная цена для участия в акции, RUB',
                           'Артикул'}

        if ozon_column_set.issubset(new_ozon_column_set):

            st.session_state['cost_ozon'] = pd.read_pickle('pages/ozon_selfcost.pkl')

            st.session_state['initial_ozon'] = st.session_state['initial_ozon'].merge(st.session_state['cost_ozon'],
                                                                                      on='Артикул')

            ct_ozon = st.session_state['initial_ozon'].copy()

            st.divider()

            try:
                ct_ozon['Категория объема/л'] = ct_ozon['Категория объема/л'].map(lambda x: math.ceil(x))

                ozon_delivery_df = pd.read_pickle('pages/ozon_delivery_fee.pkl')

                ct_ozon = ct_ozon.merge(ozon_delivery_df, on='Категория объема/л')

                ct_ozon['Текущая скидка на сайте, %'] = (100 - (
                        ct_ozon['Текущая цена'] * 100 / ct_ozon['Цена до скидки'])) / 100

                ct_ozon['Разница в скидках'] = (ct_ozon['Текущая скидка на сайте, %'] - ct_ozon[
                    'Запрашиваемая скидка по акции, %']) * 100

                ct_ozon['Текущая цена на сайте'] = ct_ozon['Цена до скидки'] - (
                        ct_ozon['Цена до скидки'] * ct_ozon['Текущая скидка на сайте, %'])

                ct_ozon['Разница в ценах'] = ct_ozon['Текущая цена'] - ct_ozon[
                    'Рассчитанная цена для участия в акции, RUB']

                ct_ozon['Отклонение текущей от РРЦ'] = ct_ozon['Текущая цена'] - ct_ozon['РРЦ']

                ct_ozon['Отклонение плановой от РРЦ'] = ct_ozon['Рассчитанная цена для участия в акции, RUB'] - ct_ozon[
                    'РРЦ']

                ct_ozon['Разница тек.откл. от план.откл.'] = ct_ozon['Отклонение текущей от РРЦ'] - ct_ozon[
                    'Отклонение плановой от РРЦ']

                ct_ozon['Комиссия (участие)'] = ct_ozon['Рассчитанная цена для участия в акции, RUB'] * 0.21

                ct_ozon['Плановая цена минус все услуги'] = ct_ozon['Рассчитанная цена для участия в акции, RUB'] - \
                                                            ct_ozon['Комиссия (участие)'] - ct_ozon['Доставка']

                ct_ozon['Результат (участие)'] = ct_ozon['Плановая цена минус все услуги'] - ct_ozon['Себестоимость']

                ct_ozon['Отклонение от РРЦ'] = ct_ozon['РРЦ'] - ct_ozon['Результат (участие)'] - ct_ozon[
                    'Себестоимость'] - ct_ozon['Комиссия (участие)'] - ct_ozon['Доставка']

                ct_ozon['Отклонение от РРЦ (%)'] = ct_ozon['Отклонение от РРЦ'] / 0.01 / ct_ozon['РРЦ']

                ct_ozon['Маржа (участие)%'] = ct_ozon['Результат (участие)'] * 100 / ct_ozon[
                    'Рассчитанная цена для участия в акции, RUB']

                ct_ozon['Решение селлера'] = ct_ozon['Маржа (участие)%'] >= ozon_margin

                ct_ozon.to_pickle('pages/ozon_presaved.pkl')

                st.dataframe(ct_ozon,
                             use_container_width=True,
                             hide_index=True,
                             column_config=ozon_clm_cfg
                             )


            except Exception as e:
                st.write(e)

        else:
            diff = ozon_column_set.difference(new_ozon_column_set)

            st.error(f'В загруженой таблице не хватает колонок: {list(diff)}')