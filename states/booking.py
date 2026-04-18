from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    choosing_language = State()
    choosing_service = State()
    choosing_preferences = State()
    choosing_warnings = State()
    choosing_date = State()
    choosing_time = State()
    confirming = State()
