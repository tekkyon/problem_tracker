import asyncio
import pprint

import aiohttp
import pandas as pd
import streamlit as st
from bitrix24 import *
from fast_bitrix24 import BitrixAsync

stages_dict = {
    'UC_4D17ON': 'Оформлена накладкная ТК',
    'UC_0UIF7U': 'Маршрутный лист',
    'UC_HJBQYB': 'Распечатан ШК',
    'FINAL_INVOICE': 'Отгружен'}

# st.set_page_config(page_title='placeholder',
#                    layout='wide',
#                    initial_sidebar_state='collapsed',
#                    page_icon=':seedling:')

WEBHOOK = 'https://greenea.bitrix24.ru/rest/10798/6yb2e79n0wrdyiwe'

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

if 'sticker_init' not in st.session_state:
    st.session_state['sticker_init'] = False

if 'stickers_df' not in st.session_state:
    st.session_state['stickers'] = {}


def get_one_deal(id: str):
    b = Bitrix24(WEBHOOK)
    lead = b.callMethod('crm.deal.get', ID=id)
    return lead


async def get_stickers_deals() -> dict:
    result = {}
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as client:
        b = BitrixAsync(WEBHOOK, client=client, verbose=True)
        deals = await b.get_all('crm.deal.list',
                                params={
                                    'select': ['ID', 'UF_CRM_1705051837784', 'STAGE_ID', 'UF_CRM_OT_PRINT'],
                                    'filter': {'STAGE_ID': ['UC_4D17ON', 'UC_0UIF7U', 'UC_HJBQYB', 'FINAL_INVOICE']}
                                })
    for deal in deals:
        result[deal['UF_CRM_1705051837784']] = {'Статус заказа': stages_dict[deal['STAGE_ID']],
                                                'ID Заказа': deal['ID'],
                                                'Этикетка': deal['UF_CRM_OT_PRINT']}

    return pd.DataFrame.from_dict(result, orient='index').reset_index()


if not st.session_state['sticker_init']:
    st.session_state['stickers'] = asyncio.run(get_stickers_deals())
    st.session_state['sticker_init'] = True
    stickers_df = st.session_state['stickers']
else:
    stickers_df = st.session_state['stickers']

    stickers_df['ID Заказа'] = stickers_df['ID Заказа'].apply(
        lambda order: f'https://greenea.bitrix24.ru/crm/deal'
                      f'/details/{order}/')


    # pprint.pprint(get_one_deal('10882'))


def render_sticker_df():
    column_cfg = {
        'index': st.column_config.TextColumn(
            'Номер заказа 1С'
        ),
        'status': st.column_config.TextColumn(
            'Статус в Битрикс'
        ),
        'ID Заказа': st.column_config.LinkColumn(
            'Bitrix ID',
            display_text="https://greenea\.bitrix24\.ru/crm/deal/details/(.*?)/",
            width='small'
        ),
        'Этикетка': st.column_config.LinkColumn(
            'Ссылка на этикетку'
        )
    }

    return st.dataframe(stickers_df,
                        hide_index=True,
                        use_container_width=True,
                        column_config=column_cfg,
                        )
