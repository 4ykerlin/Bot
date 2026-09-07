from aiogram.fsm.state import State, StatesGroup

class OrderFSM(StatesGroup):
    category = State()
    model = State()
    characteristics = State()
    condition = State()
    photo = State()