import pprint

from fast_bitrix24 import *
import aiohttp
import asyncio

from fast_bitrix24 import BitrixAsync

stages_dict = {
    'NEW': 'Новая сделка',
    'PREPAYMENT_INVOICE': 'Выставлен счет',
    'UC_6T7LQR': 'Счет оплачен',
    'PREPARATION': 'Заказ поставщику',
    'EXECUTING': 'Готов к отгрузке(собран)',
    'UC_4D17ON': 'Оформлена накладная ТК',
    '3': 'Рекламация',
    'FINAL_INVOICE': 'Отгружен'
}

webhook = 'https://greenea.bitrix24.ru/rest/10798/6yb2e79n0wrdyiwe'

# b = Bitrix(webhook)


# async def main():
#     connector = aiohttp.TCPConnector(ssl=False)
#     async with aiohttp.ClientSession(connector=connector) as client:
#         b = BitrixAsync(webhook, client=client, verbose=True)
#         user = await b.get_all('crm.deal.list')
#         print(user)

async def get_deals() -> dict:
    result = {}
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as client:
        b = BitrixAsync(webhook, client=client, verbose=True)
        deals = await b.get_all('crm.deal.list',
                                params={
                                    'select': ['ID', 'UF_CRM_1705051837784', 'STAGE_ID', 'UF_CRM_1704976176405'],
                                    'filter': {'STAGE_ID': ['PREPAYMENT_INVOICE',
                                                            'UC_6T7LQR',
                                                            'PREPARATION',
                                                            'EXECUTING',
                                                            '3',
                                                            'FINAL_INVOICE']}
                                })

    for deal in deals:
        if deal['UF_CRM_1705051837784'] is not None:
            result[deal['UF_CRM_1705051837784']] = {'Статус заказа': stages_dict[deal['STAGE_ID']],
                                                    'ID Заказа': deal['ID'],
                                                    'Габариты': deal['UF_CRM_1704976176405']}

    return result


async def get_current_status(id):
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as client:
        b = BitrixAsync(webhook, client=client, verbose=True)
        result = await b.get_all('crm.deal.list',
                                params={
                                    'select': ['STAGE_ID'],
                                    'filter': {'ID': id}
                                })
        return result


async def async_update_dimensions(id: int, dim: str):
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as client:
        b = BitrixAsync(webhook, client=client, verbose=True)
        params = {'ID': id,
                  'fields': {
                      'UF_CRM_1704976176405': dim,
                      'STAGE_ID': 'EXECUTING'
                  }}
        await b.call('crm.deal.update',
                     params)


def update_dimensions(id: int, dim: str):
    b = Bitrix(webhook)
    params = {'ID': id,
              'fields': {
                  'UF_CRM_1704976176405': dim,
                  'STAGE_ID': 'EXECUTING'
              }}
    b.call('crm.deal.update',
           params)

# def update_dimensions_v(id: int, dim: str, volume: str):
#     b = Bitrix(webhook)
#     try:
#         b.callMethod('crm.deal.update', ID=id, fields={'UF_CRM_1704976176405': dim,
#                                                        'UF_CRM_1710230198302': volume,
#                                                        'STAGE_ID': 'EXECUTING'})
#     except Exception as e:
#         print(e)
# deals_id = asyncio.run(get_deals())
# pprint.pprint(deals_id)

# status_id = asyncio.run(get_current_status(10356))
# print(status_id)


