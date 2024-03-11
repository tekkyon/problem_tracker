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

from streamlit_authenticator import Hasher

users_df_columns = ['username', 'user_id', 'role', 'location']

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


@router.message(CommandStart(),
                StateFilter(default_state),
                lambda message: message.from_user.id in render_users(DB, 'users',
                                                                     users_df_columns,
                                                                     list_mode=True,
                                                                     users='office'))
async def process_start_command(message: Message, state: FSMContext):
    register_button = InlineKeyboardButton(
        text='Зарегистрировать проблему',
        callback_data='register'
    )
    dashboard_button = InlineKeyboardButton(
        text='Дашборд',
        callback_data='dashboard'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [register_button],
        [dashboard_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        text='Этот бот создан для сбора данных о проблемах.\n\n',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.try_to_register)


@router.callback_query(StateFilter(FSMFillForm.try_to_register),
                       F.data.in_(['dashboard']),
                       lambda message: message.from_user.id in render_users(DB, 'users',
                                                                            users_df_columns,
                                                                            list_mode=True,
                                                                            users='authed'))
async def process_dashboard(callback: CallbackQuery, state: FSMContext):
    register_button = InlineKeyboardButton(
        text='Получить доступ к дашборду',
        callback_data='register_dashboard'
    )
    dashboard_button = InlineKeyboardButton(
        text='Открыть дашборд',
        url='http://31.129.33.52:8501/'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [dashboard_button],
        [register_button],
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await callback.message.answer(
        text='Для получения доступа к дашборду пройдите процедуру регистрации.',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.dashboard_login)


@router.callback_query(StateFilter(FSMFillForm.dashboard_login),
                       F.data.in_(['register_dashboard']))
async def choose_login(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Укажите желаемый логин:'
    )
    await state.set_state(FSMFillForm.login_chosen)


@router.message(StateFilter(FSMFillForm.login_chosen))
async def login_entered(message: Message, state: FSMContext):
    if message.text == '/cancel':
        await message.answer(
            text='Регистрация отменена'
        )
        await state.clear()
    else:
        await state.update_data(login=message.text)

        await message.answer(
            text='Укажите желаемый пароль:'
        )
        await state.set_state(FSMFillForm.password_chosen)


@router.message(StateFilter(FSMFillForm.password_chosen))
async def password_entered(message: Message, state: FSMContext):
    if message.text == '/cancel':
        await message.answer(
            text='Регистрация отменена'
        )
        await state.clear()

    else:
        await state.update_data(pwd=message.text)

        await message.delete()

        await message.answer(
            text='Повторите пароль:'
        )
        await state.set_state(FSMFillForm.password_repeat)


@router.message(StateFilter(FSMFillForm.password_repeat))
async def password_repeat(message: Message, state: FSMContext):
    if message.text == '/cancel':
        await message.answer(
            text='Регистрация отменена'
        )
        await state.clear()

    else:
        await state.update_data(pwd_repeat=message.text)

        username = message.from_user.first_name
        user_id = message.from_user.id

        info = await state.get_data()
        await message.delete()
        login = info['login']
        pwd = info['pwd']
        pwd_repeat = info['pwd_repeat']

        if pwd != pwd_repeat:
            await message.answer(
                text='Пароли не совпадают. Введите пароль заново:'
            )
            await state.set_state(FSMFillForm.password_chosen)
        else:
            hashed_password = Hasher([pwd_repeat]).generate()[0]
            with open('config.yaml') as file:
                config = yaml.load(file, Loader=SafeLoader)

            config['credentials']['usernames'][login] = {
                'email': f'{login}@greenea.com',
                'logged_in': False,
                'name': username,
                'password': hashed_password,
                'telegram_id': user_id,
            }
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)

            await message.answer(
                text=f'Регистрация окончена.'
            )
            await state.clear()


@router.callback_query(StateFilter(FSMFillForm.choose_department),
                       F.data.in_(['marketplace']))
async def process_authed_register_state(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Введите цифры артикула:'
    )
    await state.set_state(FSMFillForm.fill_sku_number)


@router.message(CommandStart(),
                StateFilter(default_state),
                lambda message: message.from_user.id not in render_users(DB,
                                                                         'users',
                                                                         users_df_columns,
                                                                         list_mode=True))
async def process_start_command(message: Message, state: FSMContext):
    request_auth_button = InlineKeyboardButton(
        text='Запросить авторизацию',
        callback_data='request_auth'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [request_auth_button],
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        text=f'<b>У Вас нет доступа к боту. Запросите авторизацию.</b>\n'
             f'<i>Telegram id:</i> {message.from_user.id}',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.pending)


@router.message(CommandStart(),
                StateFilter(default_state),
                lambda message: message.from_user.id not in render_users(DB,
                                                                         'users',
                                                                         users_df_columns,
                                                                         list_mode=True,
                                                                         users='authed'))
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(
        text=f'<b>У Вас еще нет доступа к боту.</b>\n'
             f'<i>Telegram id:</i> {message.from_user.id}'
    )
    await state.clear()


@router.callback_query(StateFilter(FSMFillForm.pending),
                       F.data.in_(['request_auth']),
                       lambda message: message.from_user.id not in render_users(DB,
                                                                                'users',
                                                                                users_df_columns,
                                                                                list_mode=True))
async def process_pending(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.first_name

    await add_pending_user(db=DB, username=username, user_id=user_id, table='users', role='pending')

    await callback.message.answer(
        text='Запрос отправлен.'
    )
    await state.clear()


@router.callback_query(StateFilter(FSMFillForm.try_to_register),
                       F.data.in_(['register']),
                       lambda message: message.from_user.id in render_users(DB, 'users',
                                                                            users_df_columns,
                                                                            list_mode=True,
                                                                            users='authed'))
async def process_authed_register_state(callback: CallbackQuery, state: FSMContext):
    register_marketplace = InlineKeyboardButton(
        text='Маркетплейсы',
        callback_data='marketplace'
    )
    register_b2b = InlineKeyboardButton(
        text='Б2Б',
        callback_data='b2b'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [register_marketplace],
        [register_b2b]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.answer(
        text='Укажите в каком отделе произошел брак:\n\n',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.choose_department)


@router.callback_query(StateFilter(FSMFillForm.try_to_register),
                       F.data.in_(['register']),
                       lambda message: message.from_user.id not in render_users(DB, 'users', users_df_columns,
                                                                                list_mode=True))
async def process_unauthed_register_state(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='<b>У Вас нет доступа к регистрации. Отправьте запрос на авторизацию.</b>'
    )
    await state.clear()


@router.message(Command(commands='cancel'),
                StateFilter(default_state),
                lambda message: message.from_user.id in render_users(DB, 'users',
                                                                     users_df_columns,
                                                                     list_mode=True,
                                                                     users='office')
                )
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего.\n\n'
             'Чтобы перейти к регистрации новой проблемы - '
             'отправьте команду /start'
    )


@router.message(Command(commands='cancel'),
                ~StateFilter(default_state),
                lambda message: message.from_user.id in render_users(DB, 'users',
                                                                     users_df_columns,
                                                                     list_mode=True,
                                                                     users='office')
                )
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы отменили регистрацию.\n\n'
             'Чтобы снова перейти к регистрации проблемы - '
             'отправьте команду /start'
    )
    await state.clear()


@router.callback_query(StateFilter(default_state),
                       F.data.in_(['back_to_start']),
                       lambda message: message.from_user.id in render_users(DB, 'users', users_df_columns,
                                                                            list_mode=True))
async def process_start2_command(message: Message, state: FSMContext):
    register_button = InlineKeyboardButton(
        text='Зарегистрировать проблему',
        callback_data='register'
    )
    help_button = InlineKeyboardButton(
        text='FAQ',
        callback_data='faq'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [register_button],
        [help_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        text='Этот бот создан для сбора данных о проблемах.\n\n',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.try_to_register)


@router.message(StateFilter(FSMFillForm.fill_sku_number))
async def process_sku_number_sent(message: Message, state: FSMContext):
    await state.update_data(sku_number=message.text)

    wildberries_button = InlineKeyboardButton(
        text='Wildberries',
        callback_data='wb'
    )
    ozon_button = InlineKeyboardButton(
        text='Озон',
        callback_data='ozon'
    )
    yandex_button = InlineKeyboardButton(
        text='Яндекс.Маркет',
        callback_data='ym'
    )

    sberbank_button = InlineKeyboardButton(
        text='Сбер',
        callback_data='sber'
    )
    cancel_marketplace_button = InlineKeyboardButton(
        text='Отмена',
        callback_data='cancel'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [wildberries_button, ozon_button],
        [yandex_button, sberbank_button],
        [cancel_marketplace_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    info = await state.get_data()

    await message.answer(
        text=f'<b>Выбран артикул:</b> {info["sku_number"]} \n'
             f'\n'
             f'Укажите маркетплейс:',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.fill_marketplace)


@router.callback_query(~StateFilter(default_state),
                       F.data.in_(['cancel']))
async def process_cancel_command_state(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Вы отменили регистрацию.\n\n'
             'Чтобы снова перейти к регистрации проблемы - '
             'отправьте команду /start'
    )
    await state.clear()


@router.callback_query(StateFilter(FSMFillForm.fill_marketplace),
                       F.data.in_(['wb',
                                   'ozon',
                                   'ym',
                                   'sber',
                                   'b2b']))
async def process_marketplace_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(marketplace=callback.data)

    gr_button = InlineKeyboardButton(
        text='ГР',
        callback_data='gr'
    )
    lm_button = InlineKeyboardButton(
        text='ЛМ',
        callback_data='lm'
    )
    gp_button = InlineKeyboardButton(
        text='ГП',
        callback_data='gp'
    )
    cancel_marketplace_button = InlineKeyboardButton(
        text='Отмена',
        callback_data='cancel'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [gr_button, lm_button, gp_button],
        [cancel_marketplace_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    info = await state.get_data()
    await callback.message.answer(
        text=f'<b>Выбран артикул:</b> {info["sku_number"]} \n'
             f'<b>Выбран маркет:</b> {lexicon_dict[info["marketplace"]]} \n'
             f'\n'
             f'Укажите тег маркетплейса:',
        reply_markup=markup)

    await state.set_state(FSMFillForm.fill_marketplace_type)


@router.callback_query(StateFilter(FSMFillForm.fill_marketplace_type),
                       F.data.in_(['gr',
                                   'gp',
                                   'lm'
                                   ]))
async def process_marketplace_type_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(marketplace_type=callback.data)

    info = await state.get_data()
    await callback.message.answer(
        text=f'<b>Выбран артикул:</b> {info["sku_number"]} \n'
             f'<b>Выбран маркет:</b> {lexicon_dict[info["marketplace"]]}-{info["marketplace_type"]} \n',
        reply_markup=await SimpleCalendar().start_calendar())

    await state.set_state(FSMFillForm.fill_date)


####
@router.callback_query(StateFilter(FSMFillForm.fill_date),
                       F.data.in_(['calendar']))
async def process_authed_register_state(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите дату:",
        reply_markup=await SimpleCalendar().start_calendar()
    )


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(FSMFillForm.fill_date))
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale="en_US.UTF-8", show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        defect_button = InlineKeyboardButton(
            text='Проблема с товаром',
            callback_data='defect'
        )
        package_button = InlineKeyboardButton(
            text='Проблема со сборкой',
            callback_data='bad_package'
        )
        cancel_button = InlineKeyboardButton(
            text='Отмена',
            callback_data='cancel'
        )

        keyboard: list[list[InlineKeyboardButton]] = [
            [defect_button, package_button],
            [cancel_button]
        ]

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        data = date.strftime("%d/%m/%Y")

        await state.update_data(date=data)
        info = await state.get_data()

        await callback_query.message.answer(
            text=f'<b>Выбран артикул:</b> {info["sku_number"]} \n'
                 f'<b>Выбран маркет:</b> {lexicon_dict[info["marketplace"]]}-{info["marketplace_type"]} \n'
                 f'<b>Выбрана дата:</b> {info["date"]} \n'
                 f'\n'
                 f'Выберите тип проблемы:',
            reply_markup=markup
        )

        await state.set_state(FSMFillForm.fill_type_of_problem)


@router.callback_query(StateFilter(FSMFillForm.fill_type_of_problem),
                       F.data.in_(['defect',
                                   'bad_package',
                                   ]))
async def process_type_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type_of_problem=callback.data)

    info = await state.get_data()
    await callback.message.answer(
        text=f'<b>Выбран артикул:</b> {info["sku_number"]} \n'
             f'<b>Выбран маркет:</b> {lexicon_dict[info["marketplace"]]}-{info["marketplace_type"]} \n'
             f'<b>Выбрана дата:</b> {info["date"]} \n'
             f'<b>Выбран тип проблемы:</b> {lexicon_dict[info["type_of_problem"]]} \n'
             f'\n'
             f'Напишите комментарий')

    await state.set_state(FSMFillForm.fill_comment)


@router.message(StateFilter(FSMFillForm.fill_comment))
async def process_date_sent(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)

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

    await message.answer(
        text=f'<b>Выбран артикул:</b> {info["sku_number"]} \n'
             f'<b>Выбран маркет:</b> {lexicon_dict[info["marketplace"]]}-{info["marketplace_type"]} \n'
             f'<b>Выбрана дата:</b> {info["date"]} \n'
             f'<b>Выбран тип проблемы:</b> {lexicon_dict[info["type_of_problem"]]} \n'
             f'<b>Комментарий</b>: {info["comment"]}'
             f'\n',
        reply_markup=markup
    )

    await state.set_state(FSMFillForm.summarize_state)


@router.callback_query(StateFilter(FSMFillForm.summarize_state),
                       F.data.in_(['write'
                                   ]))
async def process_save(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    info = await state.get_data()

    sku = 'digits'
    sku_number = info['sku_number']
    marketplace = info['marketplace']

    temp_date = info['date'].split('/')
    date = f'{temp_date[2]}/{temp_date[1]}/{temp_date[0]}'

    type_of_problem = info['type_of_problem']
    type_of_mp = info['marketplace_type']
    comment = info['comment']
    manager_id = callback.from_user.id
    insert_db(DB, sku, sku_number, marketplace, date,
              type_of_problem, comment, type_of_mp,
              manager_id=manager_id,
              worker='default')

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

    await callback.message.answer(
        text='<b>Информация о проблеме сохранена.</b>',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.try_to_register)


@router.callback_query(StateFilter(FSMFillForm.try_to_register),
                       F.data.in_(['test_button']),
                       lambda message: message.from_user.id in render_users(DB, 'users',
                                                                            users_df_columns,
                                                                            list_mode=True,
                                                                            users='authed'))
async def process_authed_register_state(callback: CallbackQuery, state: FSMContext):
    dict_of_buttons = read_lexicon().query('purpose == "marketplace" | key == "cancel"').set_index('key')[
        'value'].to_dict()
    keyboard = create_inline_kb(2, **dict_of_buttons)
    await callback.message.answer(
        text='Укажите маркетплейс:',
        reply_markup=keyboard
    )
    await state.set_state(FSMFillForm.keyboard_builder_test)


@router.callback_query(StateFilter(FSMFillForm.keyboard_builder_test), )
async def process_marketplace_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(marketplace=callback.data)

    info = await state.get_data()

    await callback.message.answer(
        text=f'{info["marketplace"]}'
    )
