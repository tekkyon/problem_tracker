from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message)

list_of_auth_users = [784570394]

from lexicon import lexicon_dict

from db import insert_db

storage = MemoryStorage()

router = Router()

DB = 'greenea_issues.db'


class FSMFillForm(StatesGroup):
    try_to_register = State()
    fill_sku_number = State()
    fill_marketplace = State()
    fill_marketplace_type = State()
    fill_date = State()
    fill_type_of_problem = State()
    fill_comment = State()
    summarize_state = State()
    everything_is_ok = State()


@router.message(CommandStart(),
                StateFilter(default_state),
                lambda message: message.from_user.id in list_of_auth_users)
async def process_start_command(message: Message, state: FSMContext):
    register_button = InlineKeyboardButton(
        text='Зарегистрировать проблему',
        callback_data='register'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [register_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        text='Этот бот создан для сбора данных о проблемах.\n\n',
        reply_markup=markup
    )
    await state.set_state(FSMFillForm.try_to_register)


@router.message(CommandStart(),
                StateFilter(default_state),
                lambda message: message.from_user.id not in list_of_auth_users)
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
    await state.set_state(FSMFillForm.try_to_register)


@router.callback_query(StateFilter(FSMFillForm.try_to_register),
                       F.data.in_(['register']),
                       lambda message: message.from_user.id in list_of_auth_users)
async def process_authed_register_state(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Введите цифры артикула:'
    )
    await state.set_state(FSMFillForm.fill_sku_number)


@router.callback_query(StateFilter(FSMFillForm.try_to_register),
                       F.data.in_(['faq']),
                       lambda message: message.from_user.id in list_of_auth_users)
async def process_faq_state(callback: CallbackQuery, state: FSMContext):
    back_button = InlineKeyboardButton(
        text='Назад',
        callback_data='back_to_start'
    )
    keyboard: list[list[InlineKeyboardButton]] = [
        [back_button]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await callback.message.answer(
        text='<b>Здесь будет раздел со справкой о боте</b>',
        reply_markup=markup

    )
    await state.clear()


@router.callback_query(StateFilter(FSMFillForm.try_to_register),
                       F.data.in_(['request_auth']),
                       lambda message: message.from_user.id not in list_of_auth_users)
async def process_request_auth_state(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='<b>Отправлен запрос на авторизацию в боте. После получения доступа придет уведомление.</b>'
    )
    await state.clear()


@router.callback_query(StateFilter(FSMFillForm.try_to_register),
                       F.data.in_(['register']),
                       lambda message: message.from_user.id not in list_of_auth_users)
async def process_unauthed_register_state(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='<b>У Вас нет доступа к регистрации. Отправьте запрос на авторизацию.</b>'
    )
    await state.clear()


@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего.\n\n'
             'Чтобы перейти к регистрации новой проблемы - '
             'отправьте команду /start'
    )


@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы отменили регистрацию.\n\n'
             'Чтобы снова перейти к регистрации проблемы - '
             'отправьте команду /start'
    )
    await state.clear()


@router.callback_query(StateFilter(default_state),
                       F.data.in_(['back_to_start']),
                       lambda message: message.from_user.id in list_of_auth_users)
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
    b2b_button = InlineKeyboardButton(
        text='B2B',
        callback_data='b2b'
    )
    cancel_marketplace_button = InlineKeyboardButton(
        text='Отмена',
        callback_data='cancel'
    )

    keyboard: list[list[InlineKeyboardButton]] = [
        [wildberries_button, ozon_button],
        [yandex_button, sberbank_button],
        [b2b_button, cancel_marketplace_button]
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

    await callback.message.delete()

    info = await state.get_data()
    await callback.message.answer(
        text=f'<b>Выбран артикул:</b> {info["sku_number"]} \n'
             f'<b>Выбран маркет:</b> {lexicon_dict[info["marketplace"]]}-{info["marketplace_type"]} \n'
             f'\n'
             f'Введите цифры дату в формате "дд/мм/гг"')

    await state.set_state(FSMFillForm.fill_date)


@router.message(StateFilter(FSMFillForm.fill_date))
async def process_date_sent(message: Message, state: FSMContext):
    await state.update_data(date=message.text)

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

    info = await state.get_data()
    await message.answer(
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

    await callback.message.delete()

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

    insert_db(DB, sku, sku_number, marketplace, date, type_of_problem, comment, type_of_mp)

    await callback.message.answer(
        text='<b>Информация о проблеме сохранена.</b>'
    )

    await state.clear()
