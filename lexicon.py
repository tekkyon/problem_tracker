from config import db
from db import add_lexicon

month_dict = {'January-': 'Январь',
              'February-': 'Февраль',
              'March-': 'Март',
              'April-': 'Апрель',
              'June-': 'Июнь',
              'May-': 'Май',
              'July-': 'Июль',
              'August-': 'Август',
              'September-': 'Сентябрь',
              'October-': 'Октябрь',
              'November-': 'Ноябрь',
              'December-': 'Декабрь', }

lexicon_dict = {'bad_package': 'Проблема со сборкой',
                'defect': 'Проблема с товаром',
                'wb': 'Wildberries',
                'ozon': 'Озон',
                'ym': 'Яндекс.Маркет',
                'sber': 'Сбер',
                'b2b': 'B2B',
                'nan': 'Пусто',
                'sku_number': 'Артикул'}

numerical_month_dict = {1: 'Январь',
                        2: 'Февраль',
                        3: 'Март',
                        4: 'Апрель',
                        5: 'Июнь',
                        6: 'Май',
                        7: 'Июль',
                        8: 'Август',
                        9: 'Сентябрь',
                        10: 'Октябрь',
                        11: 'Ноябрь',
                        12: 'Декабрь', }

selector_dict: dict[str, str] = {'По типу проблемы': 'Тип проблемы',
                                 'По маркетам': 'Маркетплейс'}

stat_options: list[str] = ['Общая таблица',
                           'По типу проблемы',
                           'По артикулу',
                           'По группам артикулов']

filter_options: list[str] = ['За все время',
                             'По месяцам']

columns_list: list[str] = ['sku_number',
                           'marketplace',
                           'date',
                           'type',
                           'comment']

market_buttons: dict[str, str] = {
    'btn_1': 'Wildberries',
    'btn_2': 'Озон',
    'btn_3': 'Яндекс.Маркет',
    'btn_4': 'Сбер',
    'btn_5': 'B2B',
    'cancel': 'Отмена'
}

