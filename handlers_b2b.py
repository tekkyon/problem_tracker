from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message)
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

import yaml
from yaml.loader import SafeLoader

from bot_functions import create_inline_kb
from dashboard_functions import render_users, add_pending_user

from lexicon import lexicon_dict

from db import insert_db, read_lexicon

storage = MemoryStorage()

router = Router()

DB = 'greenea_issues.db'


class FSMFillForm(StatesGroup):
    try_to_register = State()
    pending = State()
    fill_sku_number = State()
    choose_department = State()
    b2b_group_choose = State()
    b2b_sku_number_choose = State()
    b2b_order_number_choose = State()
    b2b_choose_date = State()
    b2b_fill_type_of_problem = State()
    b2b_choose_worker = State()
    b2b_fill_comment = State()
    fill_marketplace = State()
    b2b_summarize_state = State()
    fill_marketplace_type = State()
    fill_date = State()
    fill_type_of_problem = State()
    fill_comment = State()
    summarize_state = State()
    everything_is_ok = State()
    register_again = State()
    keyboard_builder_test = State()
    dashboard_login = State()
    login_chosen = State()
    password_chosen = State()
    password_repeat = State()
    pwd_and_login_ok = State()


@router.callback_query(StateFilter(FSMFillForm.choose_department),
                       F.data.in_(['b2b']))
async def choose_type_of_b2b_problem(callback: CallbackQuery,
                                     state: FSMContext):
    defect_button = InlineKeyboardButton(
        text='Проблема с товаром',
        callback_data='defect'
    )
    package_button = InlineKeyboardButton(
        text='Проблема со сборкой',
        callback_data='bad_package'
    )
    delivery_button = InlineKeyboardButton(
        text='Проблема с доставкой',
        callback_data='delivery_issue'
    )
    cancel_button = InlineKeyboardButton(
        text='Отмена',
        callback_data='cancel'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [defect_button],
        [package_button],
        [delivery_button],
        [cancel_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.answer(
        text='Какого рода проблема произошла с заказом?',
        reply_markup=markup,
    )

    await state.set_state(FSMFillForm.b2b_fill_type_of_problem)


@router.callback_query(StateFilter(FSMFillForm.b2b_fill_type_of_problem),
                       F.data.in_(['defect',
                                   'bad_package',
                                   'delivery_issue']))
async def type_of_problem_chosen(callback: CallbackQuery,
                                 state: FSMContext):
    await state.update_data(b2b_type_of_problem=callback.data)

    await callback.message.answer(
        text='Укажите номер заказа:'
    )
    await state.set_state(FSMFillForm.b2b_order_number_choose)


@router.message(StateFilter(FSMFillForm.b2b_order_number_choose))
async def order_number_chosen(message: Message,
                              state: FSMContext):
    await state.update_data(b2b_order_number=message.text)

    info = await state.get_data()

    await message.answer(
        text=f'<b>Выбран тип проблемы:</b> {lexicon_dict[info["b2b_type_of_problem"]]}\n'
             f'<b>Выбран номер заказа:</b> {info["b2b_order_number"]}\n'
             f'Укажите дату:',
        reply_markup=await SimpleCalendar().start_calendar()
    )
    await state.set_state(FSMFillForm.b2b_choose_date)


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(FSMFillForm.b2b_choose_date))
async def process_simple_b2b_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale="en_US.UTF-8", show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        data = date.strftime("%d/%m/%Y")

        await state.update_data(date=data)

        info = await state.get_data()

        fl_group_button = InlineKeyboardButton(
            text='ФЛ-',
            callback_data='fl'
        )
        ba_group_button = InlineKeyboardButton(
            text='БА-',
            callback_data='ba'
        )
        ko_group_button = InlineKeyboardButton(
            text='КО-',
            callback_data='ko'
        )
        digit_group_button = InlineKeyboardButton(
            text='Цифры',
            callback_data='digit'
        )
        cancel_button = InlineKeyboardButton(
            text='Отмена',
            callback_data='cancel'
        )

        keyboard: list[list[InlineKeyboardButton]] = [
            [fl_group_button, ba_group_button],
            [ko_group_button, digit_group_button],
            [cancel_button]
        ]

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        if info["b2b_type_of_problem"] == 'delivery_issue':

            await callback_query.message.answer(
                text=f'<b>Выбран тип проблемы:</b> {lexicon_dict[info["b2b_type_of_problem"]]}\n'
                     f'<b>Выбран номер заказа:</b> {info["b2b_order_number"]}\n'
                     f'<b>Выбрана дата:</b> {info["date"]}\n'
                     f'<b>Комментарий:</b>\n\n'
            )

            await state.set_state(FSMFillForm.b2b_fill_comment)

        else:
            await callback_query.message.answer(
                text=f'<b>Выбран тип проблемы:</b> {lexicon_dict[info["b2b_type_of_problem"]]}\n'
                     f'<b>Выбран номер заказа:</b> {info["b2b_order_number"]}\n'
                     f'<b>Выбрана дата:</b> {info["date"]}\n'
                     f'<b>Укажите группу артикулов, с которым произошла проблема:</b>\n\n',

                reply_markup=markup
            )
            await state.set_state(FSMFillForm.b2b_group_choose)


@router.callback_query(StateFilter(FSMFillForm.b2b_group_choose),
                       F.data.in_(['fl',
                                   'ba',
                                   'ko',
                                   'digit']))
async def process_b2b_sku_number_input(callback: CallbackQuery, state: FSMContext):
    await state.update_data(b2b_sku_group=callback.data)

    info = await state.get_data()

    await callback.message.answer(
        text=f'<b>Выбран тип проблемы:</b> {lexicon_dict[info["b2b_type_of_problem"]]}\n'
             f'<b>Выбран номер заказа:</b> {info["b2b_order_number"]}\n'
             f'<b>Выбрана дата:</b> {info["date"]}\n'
             f'<b>Укажите цифры артикула:</b>\n\n'
    )
    await state.set_state(FSMFillForm.b2b_sku_number_choose)


@router.message(StateFilter(FSMFillForm.b2b_sku_number_choose))
async def process_order_number(message: Message, state: FSMContext):
    await state.update_data(sku_number=message.text)

    info = await state.get_data()

    await message.answer(
        text=f'<b>Выбран тип проблемы:</b> {lexicon_dict[info["b2b_type_of_problem"]]}\n'
             f'<b>Выбран номер заказа:</b> {info["b2b_order_number"]}\n'
             f'<b>Выбрана дата:</b> {info["date"]}\n'
             f'<b>Выбран артикул:</b> {lexicon_dict[info["b2b_sku_group"]]}{info["sku_number"]}\n'
             f'<b>Укажите ответственного за сборку:</b>\n\n'

    )
    await state.set_state(FSMFillForm.b2b_choose_worker)


@router.message(StateFilter(FSMFillForm.b2b_choose_worker))
async def process_b2b_comment(message: Message, state: FSMContext):
    await state.update_data(b2b_worker=message.text)

    info = await state.get_data()

    await message.answer(
        text=f'<b>Выбран тип проблемы:</b> {lexicon_dict[info["b2b_type_of_problem"]]}\n'
             f'<b>Выбран номер заказа:</b> {info["b2b_order_number"]}\n'
             f'<b>Выбрана дата:</b> {info["date"]}\n'
             f'<b>Выбран артикул:</b> {lexicon_dict[info["b2b_sku_group"]]}{info["sku_number"]}\n'
             f'Ответственный за сборку: {info["b2b_worker"]}\n\n'
             f'Напишите комментарий к проблеме:',
    )

    await state.set_state(FSMFillForm.b2b_fill_comment)


@router.message(StateFilter(FSMFillForm.b2b_fill_comment))
async def process_date_sent(message: Message, state: FSMContext):
    await state.update_data(b2b_comment=message.text)

    info = await state.get_data()

    yes_button = InlineKeyboardButton(
        text='Сохранить в базу',
        callback_data='write'
    )
    no_button = InlineKeyboardButton(
        text='Отмена',
        callback_data='cancel'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [yes_button, no_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if info["b2b_type_of_problem"] != 'delivery_issue':
        await message.answer(
            text=f'<b>Выбран тип проблемы:</b> {lexicon_dict[info["b2b_type_of_problem"]]}\n'
                 f'<b>Выбран номер заказа:</b> {info["b2b_order_number"]}\n'
                 f'<b>Выбрана дата:</b> {info["date"]}\n'
                 f'<b>Выбран артикул:</b> {lexicon_dict[info["b2b_sku_group"]]}{info["sku_number"]}\n'
                 f'<b>Ответственный за сборку:</b> {info["b2b_worker"]}\n'
                 f'<b>Комментарий к проблеме:</b> {info["b2b_comment"]}\n\n',

            reply_markup=markup)
    else:
        await message.answer(
            text=f'<b>Выбран тип проблемы:</b> {lexicon_dict[info["b2b_type_of_problem"]]}\n'
                 f'<b>Выбран номер заказа:</b> {info["b2b_order_number"]}\n'
                 f'<b>Выбрана дата:</b> {info["date"]}\n'
                 f'<b>Комментарий к проблеме:</b> {info["b2b_comment"]}\n\n',

            reply_markup=markup
        )

    await state.set_state(FSMFillForm.b2b_summarize_state)


@router.callback_query(StateFilter(FSMFillForm.b2b_summarize_state),
                       F.data.in_(['write'
                                   ]))
async def process_b2b_save(callback: CallbackQuery, state: FSMContext):
    info = await state.get_data()

    if info["b2b_type_of_problem"] == 'delivery_issue':
        sku = ''
        sku_number = ''
        order_number = ''
        worker = ''

    else:
        sku = info["b2b_sku_group"]
        sku_number = info['sku_number']
        order_number = info["b2b_order_number"]
        worker = info["b2b_worker"]

    marketplace = 'b2b'
    temp_date = info['date'].split('/')
    date = f'{temp_date[2]}/{temp_date[1]}/{temp_date[0]}'
    type_of_problem = info['b2b_type_of_problem']
    type_of_mp = ''
    comment = info['b2b_comment']
    manager_id = callback.from_user.id
    insert_db(sku, sku_number, marketplace, date,
              type_of_problem, comment, type_of_mp,
              manager_id=manager_id,
              worker=worker,
              bitrix_id=order_number)

    reg_button = InlineKeyboardButton(
        text='Зарегистрировать новую проблему',
        callback_data='register'
    )
    dashboard_button = InlineKeyboardButton(
        text='Открыть дашборд',
        url='http://31.129.33.52:8501/'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [reg_button],
        [dashboard_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    #
    await callback.message.answer(
        text='<b>Информация о проблеме сохранена.</b>',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.try_to_register)
