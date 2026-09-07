from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_category_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Смартфон", callback_data="cat_phone")],
        [InlineKeyboardButton(text="Ноутбук", callback_data="cat_laptop")],
        [InlineKeyboardButton(text="Планшет", callback_data="cat_tablet")],
        [InlineKeyboardButton(text="Другое", callback_data="cat_other")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])

def get_order_navigation_keyboard(page: int, total_pages: int):
    buttons = []
    row = []
    if page > 0:
        row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"mgr_page_{page-1}"))
    if page < total_pages - 1:
        row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"mgr_page_{page+1}"))
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="📋 Все заявки", callback_data="mgr_all")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_order_action_keyboard(order_id: int, current_status: str):
    buttons = []
    status = current_status.lower().strip()
    if status == "new":
        buttons.append(InlineKeyboardButton(text="📥 В работу", callback_data=f"status_{order_id}_in_progress"))
    elif status == "in_progress":
        buttons.append(InlineKeyboardButton(text="💰 Назначить цену", callback_data=f"price_{order_id}"))
        buttons.append(InlineKeyboardButton(text="✅ Завершить", callback_data=f"status_{order_id}_completed"))
    elif status == "priced":
        buttons.append(InlineKeyboardButton(text="✅ Завершить", callback_data=f"status_{order_id}_completed"))
    buttons.append(InlineKeyboardButton(text="❌ Отменить заявку", callback_data=f"status_{order_id}_cancelled"))
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📈 Отчёт Excel", callback_data="admin_report")],
        [InlineKeyboardButton(text="👥 Управление менеджерами", callback_data="admin_managers")],
    ])

def get_manager_list_keyboard(managers):
    kb = []
    for mgr in managers:
        user_id, username = mgr
        text = f"@{username}" if username else f"ID {user_id}"
        kb.append([InlineKeyboardButton(text=f"❌ Снять {text}", callback_data=f"admin_remove_mgr_{user_id}")])
    kb.append([InlineKeyboardButton(text="➕ Назначить нового", callback_data="admin_add_mgr")])
    kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)