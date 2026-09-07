from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import count_users, count_orders, count_orders_by_status, get_all_orders, get_managers, set_role, get_user
from keyboards.inline import get_admin_main_keyboard, get_manager_list_keyboard
from utils.excel import create_excel_report
from utils.notify import notify_user
import os

router = Router()

class AdminAddManager(StatesGroup):
    entering_user_id = State()
    confirm = State()

async def show_admin_menu(message: Message):
    await message.answer("👑 Административная панель:", reply_markup=get_admin_main_keyboard())

@router.message(Command("admin_login"))
async def admin_login_handler(message: Message):
    from config import ADMIN_PASSWORD
    if message.text and message.text == f"/admin_login {ADMIN_PASSWORD}":
        await set_role(message.from_user.id, "admin")
        await show_admin_menu(message)
    else:
        await message.answer("Неверный пароль. Используйте /admin_login ПАРОЛЬ")

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    total_users = await count_users()
    total_orders = await count_orders()
    statuses = await count_orders_by_status()
    text = (f"📊 Статистика:\n"
            f"Пользователей: {total_users}\n"
            f"Всего заявок: {total_orders}\n"
            f"Статусы:\n" + "\n".join([f"  {k}: {v}" for k, v in statuses.items()]))
    await callback.message.edit_text(text, reply_markup=get_admin_main_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_report")
async def admin_report(callback: CallbackQuery):
    orders = await get_all_orders()
    if not orders:
        await callback.answer("Нет данных для отчёта.")
        return
    filepath = await create_excel_report(orders)
    await callback.message.answer_document(FSInputFile(filepath), caption="📄 Отчёт по заявкам")
    os.remove(filepath)
    await callback.answer()

@router.callback_query(F.data == "admin_managers")
async def admin_managers(callback: CallbackQuery):
    managers = await get_managers()
    kb = get_manager_list_keyboard(managers)
    await callback.message.edit_text("👥 Список менеджеров:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("admin_remove_mgr_"))
async def admin_remove_manager(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[3])
    await set_role(user_id, "user")
    await callback.answer("Права менеджера сняты.")
    await admin_managers(callback)

@router.callback_query(F.data == "admin_add_mgr")
async def admin_add_manager(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminAddManager.entering_user_id)
    await callback.message.edit_text("Введите Telegram ID нового менеджера (число):")
    await callback.answer()

@router.message(StateFilter(AdminAddManager.entering_user_id))
async def process_add_manager_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число (Telegram ID).")
        return
    user_id = int(message.text)
    user = await get_user(user_id)
    if not user:
        await message.answer("Пользователь с таким ID не зарегистрирован в боте. Попросите его написать /start.")
        return
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminAddManager.confirm)
    await message.answer(f"Назначить пользователя @{user[1] if user[1] else 'без username'} менеджером? (да/нет)")

@router.message(StateFilter(AdminAddManager.confirm))
async def confirm_add_manager(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        data = await state.get_data()
        await set_role(data['target_user_id'], "manager")
        await message.answer("✅ Менеджер назначен.")
        await notify_user(data['target_user_id'], "🎉 Вам назначена роль менеджера в боте.")
    else:
        await message.answer("Отменено.")
    await state.clear()
    managers = await get_managers()
    kb = get_manager_list_keyboard(managers)
    await message.answer("Список менеджеров:", reply_markup=kb)

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    await show_admin_menu(callback.message)
    await callback.answer()