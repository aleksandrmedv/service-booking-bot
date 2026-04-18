from aiogram import F, Router
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import MAP_LINK, MASTER_USERNAME
from keyboards.main import get_main_menu_keyboard, get_services_keyboard
from utils.texts import TEXTS

router = Router()


async def get_lang(state: FSMContext) -> str | None:
    data = await state.get_data()
    return data.get("lang")


@router.message(F.text)
async def handle_menu(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if not lang:
        raise SkipHandler()

    if message.text == TEXTS[lang]["services"]:
        await message.answer(
            TEXTS[lang]["choose_service"],
            reply_markup=get_services_keyboard(lang),
        )
        return

    if message.text == TEXTS[lang]["address"]:
        await message.answer(
            f"{TEXTS[lang]['map_message']}\n{MAP_LINK}",
            reply_markup=get_main_menu_keyboard(lang),
        )
        return

    if message.text == TEXTS[lang]["contact"]:
        await message.answer(
            f"{TEXTS[lang]['contact_message']}\nhttps://t.me/{MASTER_USERNAME}",
            reply_markup=get_main_menu_keyboard(lang),
        )
        return

    raise SkipHandler()
