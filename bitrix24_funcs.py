from bitrix24 import *
# import pprint
#
#
# stages_dict = {
#     'NEW': 'Новая сделка',
#     'PREPAYMENT_INVOICE': 'Выставлен счет',
#     'UC_6T7LQR': 'Счет оплачен',
#     'PREPARATION': 'Заказ поставщику',
#     'EXECUTING': 'Готов к отгрузке(собран)',
#     'UC_4D17ON': 'Оформлена накладная ТК',
#     'UC_HJBQYB': 'Распечатан ШК',
# }
#
WEBHOOK = 'https://greenea.bitrix24.ru/rest/10798/6yb2e79n0wrdyiwe'

b = Bitrix24(WEBHOOK)
#
#
# # leads = b.callMethod('crm.deal.update', ID='10536', fields={'UF_CRM_1704976176405': 'test3'})
# # leads = b.callMethod('crm.deal.get', ID='10484')
# # lead = b.callMethod('crm.deal.get', ID='10882')
# # pprint.pprint(lead)
#
# # 'UF_CRM_1710230198302'
# def get_deals_id():
#     return b.callMethod('crm.deal.list', filter={'STAGE_ID': ['PREPAYMENT_INVOICE',
#                                                               'UC_6T7LQR',
#                                                               'PREPARATION',
#                                                               'EXECUTING']})
#
# def get_deals_id_for_printer():
#     return b.callMethod('crm.deal.list', filter={'STAGE_ID': ['UC_4D17ON',
#                                                               'UC_HJBQYB']})
#
#
#
# def init_1c_orders() -> dict:
#     deal_ids = []
#     deals = get_deals_id()
#     for deal in deals:
#         deal_ids.append(deal["ID"])
#
#     result = {}
#     for id in deal_ids:
#         temp = b.callMethod('crm.deal.get', ID=id)
#         if 'UF_CRM_1705051837784' in temp and len(temp['UF_CRM_1705051837784']) > 0:
#             result[temp['UF_CRM_1705051837784']] = {'ID Заказа': temp["ID"],
#                                                     'Статус заказа': stages_dict[temp["STAGE_ID"]],
#                                                     'Габариты': temp['UF_CRM_1704976176405']
#                                                     }
#     return result
#
# pprint.pprint(get_deals_id())
#
# def init_stickers():
#     deal_ids = []
#     deals = get_deals_id_for_printer()
#
#     for deal in deals:
#         deal_ids.append(deal['ID'])
#
#     result = {}
#     for id in deal_ids:
#         temp = b.callMethod('crm.deal.get', ID=id)
#         result[temp['UF_CRM_1705051837784']] = {'ID Заказа': temp["ID"],
#                                                     'Статус заказа': stages_dict[temp["STAGE_ID"]],
#                                                 'Ссылка на этикетку': temp['UF_CRM_OT_PRINT']
#                                                     }
#
#     return result
#
# # for id in deal_ids:
# #     result = b.callMethod('crm.deal.get', ID=id)
# #     if 'UF_CRM_1705051837784' in result and len(result['UF_CRM_1705051837784']) > 0:
# #         print(f'ID Заказа: {result["ID"]}')
# #         print(f'Статус заказа: {stages_dict[result["STAGE_ID"]]}')
# #         print(f'Номер заказа 1С: {result["UF_CRM_1705051837784"]}')
# #         print(f'Габариты: {result["UF_CRM_1704976176405"]}')
# #         print()
#
#
def update_dimensions_v(id: int, dim: str, volume: str):
    try:
        b.callMethod('crm.deal.update', ID=id, fields={'UF_CRM_1704976176405': dim,
                                                       'UF_CRM_1710230198302': volume,
                                                       'STAGE_ID': 'EXECUTING'})
    except Exception as e:
        print(e)
#
#
# # update_dimensions(10500, 'тест')
#
# # def get_deal_by_number(id: int):
# #     result = b.callMethod('crm.deal.list', params={'filter': {'UF_CRM_1705051837784': "8098"}})
# #     return result
# #
# # print(get_deal_by_number(8098))
#
#
