from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.main import get_language_keyboard, get_main_menu_keyboard
from states.booking import BookingStates
from utils.texts import LANGUAGE_BY_BUTTON, TEXTS

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BookingStates.choosing_language)
    await message.answer(
        TEXTS["en"]["choose_language"],
        reply_markup=get_language_keyboard(),
    )


@router.message(BookingStates.choosing_language, F.text.in_(LANGUAGE_BY_BUTTON.keys()))
async def choose_language(message: Message, state: FSMContext) -> None:
    lang = LANGUAGE_BY_BUTTON[message.text]
    await state.update_data(lang=lang)
    await state.set_state(BookingStates.choosing_service)
    await message.answer(
        f"{TEXTS[lang]['language_saved']}\n\n{TEXTS[lang]['main_menu_prompt']}",
        reply_markup=get_main_menu_keyboard(lang),
    )


@router.message(BookingStates.choosing_language)
async def invalid_language(message: Message) -> None:
    await message.answer(
        TEXTS["en"]["invalid_choice"],
        reply_markup=get_language_keyboard(),
    )
