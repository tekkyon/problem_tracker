from bitrix24 import *

stages_dict = {
    'NEW': 'Новая сделка',
    'PREPAYMENT_INVOICE': 'Выставлен счет',
    'UC_6T7LQR': 'Счет оплачен',
    'PREPARATION': 'Заказ поставщику',
    'EXECUTING': 'Готов к отгрузке(собран)',
    'UC_4D17ON': 'Оформлена накладная ТК'
}

WEBHOOK = 'https://greenea.bitrix24.ru/rest/10798/6yb2e79n0wrdyiwe'

b = Bitrix24(WEBHOOK)


# leads = b.callMethod('crm.deal.update', ID='10536', fields={'UF_CRM_1704976176405': 'test3'})
# leads = b.callMethod('crm.deal.get', ID='10484')
def get_deals_id():
    return b.callMethod('crm.deal.list', filter={'STAGE_ID': ['PREPAYMENT_INVOICE',
                                                              'UC_6T7LQR',
                                                              'PREPARATION',
                                                              'EXECUTING']})


def init_1c_orders() -> dict:
    deal_ids = []
    deals = get_deals_id()
    for deal in deals:
        deal_ids.append(deal["ID"])

    result = {}
    for id in deal_ids:
        temp = b.callMethod('crm.deal.get', ID=id)
        if 'UF_CRM_1705051837784' in temp and len(temp['UF_CRM_1705051837784']) > 0:
            result[temp['UF_CRM_1705051837784']] = {'ID Заказа': temp["ID"],
                                                    'Статус заказа': stages_dict[temp["STAGE_ID"]],
                                                    'Габариты': temp['UF_CRM_1704976176405']
                                                    }
    return result


# for id in deal_ids:
#     result = b.callMethod('crm.deal.get', ID=id)
#     if 'UF_CRM_1705051837784' in result and len(result['UF_CRM_1705051837784']) > 0:
#         print(f'ID Заказа: {result["ID"]}')
#         print(f'Статус заказа: {stages_dict[result["STAGE_ID"]]}')
#         print(f'Номер заказа 1С: {result["UF_CRM_1705051837784"]}')
#         print(f'Габариты: {result["UF_CRM_1704976176405"]}')
#         print()


def update_dimensions(id: int, dim: str):
    b.callMethod('crm.deal.update', ID=id, fields={'UF_CRM_1704976176405': dim})


# update_dimensions(10500, 'тест')

# def get_deal_by_number(id: int):
#     result = b.callMethod('crm.deal.list', params={'filter': {'UF_CRM_1705051837784': "8098"}})
#     return result
#
# print(get_deal_by_number(8098))
