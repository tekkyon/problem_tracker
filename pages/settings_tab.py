import streamlit as st
import pandas as pd
import math

def render_setting_tab():
    setting_col = st.columns([1, 1])

    with setting_col[0]:
        with st.expander('Загрузить новые данные для Wildberries'):
            wb_selfcost = st.file_uploader(label='Сюда загружается таблица себестоимости WB', type='xlsx')

            wb_delivery = st.file_uploader(label='Таблица с коэффицентами доставки WB', type='xlsx')

        if wb_selfcost is not None:
            wb_selfcost_df = pd.read_excel(wb_selfcost)

            if set(wb_selfcost_df.columns) == {'Артикул wildberries',
                                               'Артикул поставщика',
                                               'Вес, г',
                                               'РРЦ',
                                               'Глубина, мм',
                                               'Себестоимость',
                                               'Ширина, мм',
                                               'Высота, мм',
                                               'МРЦ'}:
                wb_selfcost_df['Категория объема/л'] = wb_selfcost_df['Высота, мм'] * wb_selfcost_df['Ширина, мм'] * \
                                                       wb_selfcost_df[
                                                           'Глубина, мм'] / 1000000

                wb_selfcost_df['Категория объема/л'] = wb_selfcost_df['Категория объема/л'].map(lambda x: math.ceil(x))

                wb_selfcost_df.to_pickle('pages/wb_selfcost.pkl')
                st.success('Данные о себестоимости обновлены')
            else:
                st.error(
                    """'Артикул wildberries',
                     'Артикул поставщика',
                      'Вес, г',
                       'РРЦ',
                        'Глубина, мм',
                         'Себестоимость',
                          'Ширина, мм',
                           'Высота, мм',
                            'МРЦ' - необходимые колонки в загружаемой таблице""")

        if wb_delivery is not None:
            wb_delivery_df = pd.read_excel(wb_delivery)

            if set(wb_delivery_df.columns) == {'Доставка', 'Категория объема/л'}:
                wb_delivery_df.to_pickle('pages/wb_delivery_fee.pkl')
                st.success('Данные о доставке обновлены')

            else:
                st.error("'Категория объема/л', 'Доставка' - необходимый формат колонок в загружаемой таблице")

        with st.container(border=True):
            st.caption('Данные для Wildberries')
            wb_selfcost_saved = pd.read_pickle('pages/wb_selfcost.pkl')
            st.dataframe(wb_selfcost_saved, use_container_width=True, hide_index=True)

            wb_delivery_fee_saved = pd.read_pickle('pages/wb_delivery_fee.pkl')
            st.dataframe(wb_delivery_fee_saved, use_container_width=True, hide_index=True)

    with setting_col[1]:
        with st.expander('Загрузить новые данные для Ozon'):
            ozon_selfcost = st.file_uploader(label='Сюда загружается таблица себестоимости Ozon', type='xlsx')

            ozon_delivery = st.file_uploader(label='Таблица с коэффицентами доставки Ozon', type='xlsx')

        if ozon_selfcost is not None:
            ozon_selfcost_df = pd.read_excel(ozon_selfcost)
            if set(ozon_selfcost_df.columns) == {'РРЦ', 'Себестоимость', 'Артикул', 'Категория объема/л'}:
                ozon_selfcost_df.to_pickle('pages/ozon_selfcost.pkl')
                st.success('Данные о себестоимости обновлены')
            else:
                st.error("'РРЦ', 'Себестоимость', 'Артикул' - необходимый формат колонок в загружаемой таблице")
        if ozon_delivery is not None:
            ozon_delivery_df = pd.read_excel(ozon_delivery)
            if set(ozon_delivery_df.columns) == {'Доставка', 'Категория объема/л'}:
                ozon_delivery_df.to_pickle('pages/ozon_delivery_fee.pkl')
                st.success('Данные о доставке обновлены')
            else:
                st.error("'Категория объема/л', 'Доставка' - необходимый формат колонок в загружаемой таблице")

        with st.container(border=True):
            st.caption('Данные для Ozon')
            ozon_selfcost_saved = pd.read_pickle('pages/ozon_selfcost.pkl')
            st.dataframe(ozon_selfcost_saved, use_container_width=True, hide_index=True)

            ozon_delivery_fee_saved = pd.read_pickle('pages/ozon_delivery_fee.pkl')
            st.dataframe(ozon_delivery_fee_saved, use_container_width=True, hide_index=True)