from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_orders, get_order, update_order_status, get_user, get_all_orders
from keyboards.inline import get_order_navigation_keyboard, get_order_action_keyboard
from utils.notify import notify_user
import math

router = Router()

class ManagerPriceFSM(StatesGroup):
    entering_price = State()

async def show_orders(message: Message, page: int):
    total_orders = await get_all_orders()
    total_pages = math.ceil(len(total_orders) / 3) if total_orders else 1
    offset = page * 3
    orders = await get_orders(limit=3, offset=offset)
    if not orders:
        await message.answer("Нет заявок.")
        return
    for order in orders:
        text = (f"📋 Заявка #{order[0]}\n"
                f"Категория: {order[2]}\n"
                f"Модель: {order[3]}\n"
                f"Состояние: {order[5]}\n"
                f"Статус: {order[7]}\n"
                f"Цена: {order[8] if order[8] else 'не назначена'}")
        keyboard = get_order_action_keyboard(order[0], order[7])
        await message.answer(text, reply_markup=keyboard)
        if order[6]:
            await message.answer_photo(photo=order[6], caption="Фото устройства")
    nav_kb = get_order_navigation_keyboard(page, total_pages)
    if nav_kb:
        await message.answer("Навигация:", reply_markup=nav_kb)

@router.message(Command("manager_login"))
async def manager_login_simple(message: Message):
    user = await get_user(message.from_user.id)
    if user and user[2] == "manager":
        await show_orders(message, page=0)
    else:
        await message.answer("У вас нет прав менеджера. Обратитесь к администратору.")

@router.callback_query(F.data.startswith("mgr_page_"))
async def mgr_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    await show_orders(callback.message, page)
    await callback.answer()

@router.callback_query(F.data.startswith("status_"))
async def change_status(callback: CallbackQuery):
    parts = callback.data.split("_")
    order_id = int(parts[1])
    new_status = parts[2]
    
    # 🔥 КОСТЫЛЬ: если пришло 'in' – исправляем на 'in_progress'
    if new_status == "in":
        new_status = "in_progress"
        print(f"🔧 Исправлен статус: 'in' -> 'in_progress'")
    
    order = await get_order(order_id)
    if not order:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return
    current_status = order[7]
    if current_status == new_status:
        await callback.answer("Статус уже установлен.", show_alert=True)
        return
    await update_order_status(order_id, new_status)
    user_id = order[1]
    status_names = {
        "in_progress": "В работе",
        "completed": "Завершена",
        "cancelled": "Отменена"
    }
    status_text = status_names.get(new_status, new_status)
    await notify_user(user_id, f"📢 Статус вашей заявки #{order_id} изменён на '{status_text}'.")
    await callback.answer(f"Статус изменён на {status_text}")
    await callback.message.edit_reply_markup(reply_markup=get_order_action_keyboard(order_id, new_status))

@router.callback_query(F.data.startswith("price_"))
async def ask_price(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[1])
    await state.update_data(order_id=order_id)
    await state.set_state(ManagerPriceFSM.entering_price)
    await callback.message.answer("Введите сумму (только цифры):")
    await callback.answer()

@router.message(StateFilter(ManagerPriceFSM.entering_price))
async def set_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите число, например 15000.")
        return
    price = int(message.text)
    data = await state.get_data()
    order_id = data['order_id']
    await update_order_status(order_id, "priced", price)
    order = await get_order(order_id)
    if order:
        user_id = order[1]
        await notify_user(user_id, f"💰 Менеджер назначил цену за заявку #{order_id}: {price} руб.")
    await state.clear()
    await message.answer(f"✅ Цена {price} назначена для заявки #{order_id}.")
    await show_orders(message, page=0)