from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message)
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

import lexicon
from bitrix24_funcs import init_1c_orders, update_dimensions
from bitrix2sql import create_orders_kb, init_keyboard_dct
from bot_functions import create_inline_kb
from config import db
from dashboard_functions import render_users, add_pending_user

storage = MemoryStorage()

router = Router()

users_df_columns = ['username', 'user_id', 'role', 'location']


class FSMFillForm(StatesGroup):
    try_to_register_dims = State()
    choose_order_state = State()
    enter_qny_of_box = State()
    enter_dims_of_only_box = State()
    enter_dims_of_1st_box = State()
    enter_dims_of_2nd_box = State()
    save_dims_of_box = State()


@router.message(CommandStart(),
                StateFilter(default_state),
                lambda message: message.from_user.id in render_users(db, 'users',
                                                                     users_df_columns,
                                                                     list_mode=True,
                                                                     users='warehouse'))
async def process_start_register_dims(message: Message, state: FSMContext):
    register_dims_button = InlineKeyboardButton(
        text='Внести габариты',
        callback_data='register_dims'
    )

    feedback_button = InlineKeyboardButton(
        text='Обратная связь',
        url='https://t.me/tekkyon'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [register_dims_button],
        [feedback_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        text='Этот бот создан для сбора данных о габаритах.\n\n',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.try_to_register_dims)


@router.callback_query(StateFilter(FSMFillForm.try_to_register_dims),
                       F.data.in_(['register_dims']),
                       lambda message: message.from_user.id in render_users(db, 'users',
                                                                            users_df_columns,
                                                                            list_mode=True,
                                                                            users='warehouse'))
async def process_authed_register_state(callback: CallbackQuery, state: FSMContext):
    buts = init_keyboard_dct(db, limit=20)

    keyboard = create_inline_kb(4, **buts)

    await callback.message.answer(
        text=f'Выберите заказ:',
        reply_markup=keyboard
    )

    await state.set_state(FSMFillForm.choose_order_state)


@router.message(Command(commands='cancel'),
                ~StateFilter(default_state),
                lambda message: message.from_user.id in render_users(db, 'users',
                                                                     users_df_columns,
                                                                     list_mode=True,
                                                                     users='warehouse')
                )
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы отменили регистрацию габаритов.\n\n'
             'Чтобы снова перейти к регистрации габаритов - '
             'отправьте команду /start'
    )
    await state.clear()


@router.message(Command(commands='cancel'),
                StateFilter(default_state),
                lambda message: message.from_user.id in render_users(db, 'users',
                                                                     users_df_columns,
                                                                     list_mode=True,
                                                                     users='warehouse')
                )
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего.\n\n'
             'Чтобы снова перейти к регистрации габаритов - '
             'отправьте команду /start'
    )


@router.callback_query(StateFilter(FSMFillForm.choose_order_state))
async def process_order(callback: CallbackQuery, state: FSMContext):
    await state.update_data(order_id=callback.data)

    info = await state.get_data()

    buts = {
        '1': '1',
        '2': '2',
        '3': '3',
        '4': '4',
        '5': '5',
        '6': '6',
        '7': '7',
        '>7': '>7'}

    keyboard = create_inline_kb(4, **buts)

    await callback.message.answer(
        text=f'Выбран заказ: <b>{info["order_id"][-11:]}</b> \n\n'
             'Введите количество мест:',
        reply_markup=keyboard
    )

    await state.set_state(FSMFillForm.enter_qny_of_box)


@router.callback_query(StateFilter(FSMFillForm.enter_qny_of_box),
                       F.data.in_(['2', '3', '4', '5', '6', '7']))
async def process_qny_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(qny_of_box=callback.data)

    info = await state.get_data()

    await callback.message.answer(
        text=f'Выбран заказ: <b>{info["order_id"][-11:]}</b> \n'
             f'Количество мест: <b>{info["qny_of_box"]}</b>\n\n'
             'Введите размеры первого места:'
    )
    await state.set_state(FSMFillForm.enter_dims_of_1st_box)


@router.message(StateFilter(FSMFillForm.enter_dims_of_1st_box))
async def process_first_box_dims_sent(message: Message, state: FSMContext):
    await state.update_data(dims_of_1st_box=message.text)

    info = await state.get_data()

    same_box = InlineKeyboardButton(
        text='Аналогичны предыдущему месту',
        callback_data='same'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [same_box]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        text=f'Выбран заказ: <b>{info["order_id"][-11:]}</b> \n'
             f'Количество мест: <b>{info["qny_of_box"]}</b> \n'
             f'Габариты первого места: <b>{info["dims_of_1st_box"]}</b>\n\n'
             'Введите габариты второго места:',
        reply_markup=markup
    )
    if info["qny_of_box"] == '2':
        await state.set_state(FSMFillForm.enter_dims_of_only_box)
    else:
        await state.set_state(FSMFillForm.enter_dims_of_2nd_box)

@router.message(StateFilter(FSMFillForm.enter_dims_of_2nd_box))
async def process_first_box_dims_sent(message: Message, state: FSMContext):
    await state.update_data(dims_of_1st_box=message.text)

    info = await state.get_data()

    same_box = InlineKeyboardButton(
        text='Аналогичны предыдущему месту',
        callback_data='same'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [same_box]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        text=f'Выбран заказ: <b>{info["order_id"][-11:]}</b> \n'
             f'Количество мест: <b>{info["qny_of_box"]}</b> \n'
             f'Габариты первого места: <b>{info["dims_of_1st_box"]}</b>\n'
             f'Габариты второго места: <b>{info["dims_of_1st_box"]}</b>\n\n'
             'Введите габариты второго места:',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.enter_dims_of_3rd_box)

# @router.callback_query(StateFilter(FSMFillForm.enter_dims_of_2nd_box),
#                        F.data.in_(['same']))
# async def process_2nd_box_sent(callback: CallbackQuery, state: FSMContext):
#
#     info = await state.get_data()
#     lastbox = info["dims_of_1st_box"]
#     await state.update_data(dims_of_1st_box=lastbox)





@router.callback_query(StateFilter(FSMFillForm.enter_qny_of_box),
                       F.data.in_(['1']))
async def process_qny_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(qny_of_box=callback.data)

    info = await state.get_data()

    await callback.message.answer(
        text=f'Выбран заказ: <b>{info["order_id"][-11:]}</b> \n'
             f'Количество мест: <b>{info["qny_of_box"]}</b>\n\n'
             'Введите размеры и вес места:'
    )
    await state.set_state(FSMFillForm.enter_dims_of_only_box)


@router.message(StateFilter(FSMFillForm.enter_dims_of_only_box))
async def process_dims_sent(message: Message, state: FSMContext):
    await state.update_data(dims_of_box=message.text)

    info = await state.get_data()

    yes_button = InlineKeyboardButton(
        text='Сохранить в базу',
        callback_data='save'
    )
    no_button = InlineKeyboardButton(
        text='Отмена',
        callback_data='cancel'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [yes_button, no_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        text=f'Выбран заказ: <b>{info["order_id"][-11:]}</b> \n'
             f'Количество мест: <b>{info["qny_of_box"]}</b> \n'
             f'Габариты мест: <b>{info["dims_of_box"]}</b>\n\n'
             f'Внести габариты в битрикс24?',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.save_dims_of_box)


@router.callback_query(StateFilter(FSMFillForm.save_dims_of_box),
                       F.data.in_(['save'
                                   ]))
async def process_save(callback: CallbackQuery, state: FSMContext):
    info = await state.get_data()

    order_id = int(info["order_id"].split('_')[0])
    dims = info["dims_of_box"]

    update_dimensions(order_id, dims)

    await callback.message.answer(
        text='<b>Габариты сохранены.</b>'
    )
    await state.set_state(FSMFillForm.try_to_register_dims)
