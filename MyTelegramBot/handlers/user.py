from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from states.order_states import OrderFSM
from keyboards.inline import get_category_keyboard, get_cancel_keyboard
from database import add_order, set_user
from utils.validators import is_valid_text
from utils.notify import notify_managers

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    await set_user(user_id, username)
    await message.answer(
        "👋 Добро пожаловать в сервис по оценке техники!\n"
        "Чтобы создать заявку, нажмите /new_order"
    )

@router.message(Command("new_order"), default_state)
async def cmd_new_order(message: Message, state: FSMContext):
    await state.set_state(OrderFSM.category)
    await message.answer("Выберите категорию техники:", reply_markup=get_category_keyboard())

@router.callback_query(StateFilter(OrderFSM.category), F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    await state.set_state(OrderFSM.model)
    await callback.message.edit_text("Введите модель устройства (например, iPhone 13):", reply_markup=get_cancel_keyboard())
    await callback.answer()

@router.message(StateFilter(OrderFSM.model))
async def process_model(message: Message, state: FSMContext):
    if not is_valid_text(message.text, min_len=2):
        await message.answer("Модель должна содержать минимум 2 символа. Попробуйте снова.")
        return
    await state.update_data(model=message.text)
    await state.set_state(OrderFSM.characteristics)
    await message.answer("Введите характеристики (процессор, память, диагональ и т.д.):", reply_markup=get_cancel_keyboard())

@router.message(StateFilter(OrderFSM.characteristics))
async def process_characteristics(message: Message, state: FSMContext):
    if not is_valid_text(message.text, min_len=3):
        await message.answer("Характеристики должны быть не короче 3 символов.")
        return
    await state.update_data(characteristics=message.text)
    await state.set_state(OrderFSM.condition)
    await message.answer("Опишите состояние техники (новая, б/у, царапины и т.д.):", reply_markup=get_cancel_keyboard())

@router.message(StateFilter(OrderFSM.condition))
async def process_condition(message: Message, state: FSMContext):
    if not is_valid_text(message.text, min_len=3):
        await message.answer("Состояние должно быть описано подробнее (минимум 3 символа).")
        return
    await state.update_data(condition=message.text)
    await state.set_state(OrderFSM.photo)
    await message.answer("Теперь отправьте фото устройства (одно фото):", reply_markup=get_cancel_keyboard())

@router.message(StateFilter(OrderFSM.photo))
async def process_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте именно фото (не текст и не документ).")
        return
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    order_id = await add_order(
        user_id=message.from_user.id,
        category=data['category'],
        model=data['model'],
        characteristics=data['characteristics'],
        condition=data['condition'],
        photo_file_id=photo_file_id
    )
    await state.clear()
    await message.answer(f"✅ Заявка #{order_id} создана! Менеджер свяжется с вами в ближайшее время.")
    await notify_managers(f"🆕 Новая заявка #{order_id} от пользователя @{message.from_user.username or 'без username'}")

@router.callback_query(F.data == "cancel")
async def cancel_process(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Создание заявки отменено.")
    await callback.answer()