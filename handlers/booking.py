from datetime import date, datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from config import ADMIN_ID
from data import PREFERENCES, SERVICES, TIME_SLOTS, WARNINGS
from keyboards.main import (
    get_confirmation_keyboard,
    get_date_keyboard,
    get_main_menu_keyboard,
    get_preferences_keyboard,
    get_services_keyboard,
    get_time_keyboard,
    get_warnings_keyboard,
)
from states.booking import BookingStates
from utils.texts import TEXTS

router = Router()


def get_service_by_button(text: str, lang: str) -> dict | None:
    for service in SERVICES:
        label = TEXTS[lang]["service_with_price"].format(
            name=service["name"][lang],
            price=service["price"],
        )
        if text == label:
            return service
    return None

def parse_manual_date(value: str) -> str | None:
    cleaned = value.strip()
    for pattern in ("%d.%m.%Y", "%d.%m.%y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(cleaned, pattern).strftime("%d.%m.%Y")
        except ValueError:
            continue
    return None


def get_item_by_text(items: list[dict], text: str, lang: str) -> dict | None:
    for item in items:
        if item["text"][lang] == text:
            return item
    return None


def normalize_date_button_text(text: str) -> str:
    prefixes = ("✅ ", "☑️ ")
    for prefix in prefixes:
        if text.startswith(prefix):
            return text[len(prefix):]
    return text


async def build_summary(data: dict) -> str:
    lang = data["lang"]
    service = next(item for item in SERVICES if item["id"] == data["service_id"])
    preferences = data.get("preferences") or TEXTS[lang]["skip"]
    warnings = data.get("warnings") or TEXTS[lang]["none"]
    lines = [
        TEXTS[lang]["summary_title"],
        "",
        TEXTS[lang]["summary_service"].format(value=service["name"][lang]),
        TEXTS[lang]["summary_date"].format(value=data["date"]),
        TEXTS[lang]["summary_time"].format(value=data["time"]),
        TEXTS[lang]["summary_preferences"].format(value=preferences),
        TEXTS[lang]["summary_warnings"].format(value=warnings),
    ]
    return "\n".join(lines)


def build_admin_message(data: dict, user: Message) -> str:
    lang = data["lang"]
    service = next(item for item in SERVICES if item["id"] == data["service_id"])
    username = f"@{user.from_user.username}" if user.from_user.username else "-"
    preferences = data.get("preferences") or TEXTS[lang]["skip"]
    warnings = data.get("warnings") or TEXTS[lang]["none"]
    lines = [
        TEXTS[lang]["booking_admin_title"],
        TEXTS[lang]["booking_admin_username"].format(value=username),
        TEXTS[lang]["booking_admin_user_id"].format(value=user.from_user.id),
        TEXTS[lang]["summary_service"].format(value=service["name"][lang]),
        TEXTS[lang]["summary_date"].format(value=data["date"]),
        TEXTS[lang]["summary_time"].format(value=data["time"]),
        TEXTS[lang]["summary_preferences"].format(value=preferences),
        TEXTS[lang]["summary_warnings"].format(value=warnings),
    ]
    return "\n".join(lines)


@router.message(BookingStates.choosing_service, F.text)
async def choose_service(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang")
    if not lang:
        await message.answer(TEXTS["en"]["missing_language"])
        return

    service = get_service_by_button(message.text, lang)
    if not service:
        await message.answer(
            TEXTS[lang]["invalid_choice"],
            reply_markup=get_services_keyboard(lang),
        )
        return

    await state.update_data(service_id=service["id"])
    await state.set_state(BookingStates.choosing_preferences)
    await state.update_data(preferences_custom=False, warnings_custom=False)
    await message.answer(
        TEXTS[lang]["choose_preferences"],
        reply_markup=get_preferences_keyboard(lang),
    )


@router.message(BookingStates.choosing_preferences, F.text)
async def choose_preferences(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data["lang"]
    selected = get_item_by_text(PREFERENCES, message.text, lang)

    if selected:
        await state.update_data(preferences=selected["text"][lang], preferences_custom=False)
        await state.set_state(BookingStates.choosing_warnings)
        await message.answer(
            TEXTS[lang]["choose_warnings"],
            reply_markup=get_warnings_keyboard(lang),
        )
        return

    if message.text == TEXTS[lang]["custom_input"]:
        await state.update_data(preferences_custom=True)
        await message.answer(TEXTS[lang]["enter_preferences"])
        return

    if message.text == TEXTS[lang]["skip"]:
        await state.update_data(preferences=TEXTS[lang]["skip"], preferences_custom=False)
        await state.set_state(BookingStates.choosing_warnings)
        await message.answer(
            TEXTS[lang]["choose_warnings"],
            reply_markup=get_warnings_keyboard(lang),
        )
        return

    if data.get("preferences_custom"):
        await state.update_data(preferences=message.text.strip(), preferences_custom=False)
        await state.set_state(BookingStates.choosing_warnings)
        await message.answer(
            TEXTS[lang]["choose_warnings"],
            reply_markup=get_warnings_keyboard(lang),
        )
        return

    await message.answer(
        TEXTS[lang]["invalid_choice"],
        reply_markup=get_preferences_keyboard(lang),
    )


@router.message(BookingStates.choosing_warnings, F.text)
async def choose_warnings(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data["lang"]
    selected = get_item_by_text(WARNINGS, message.text, lang)

    if selected:
        await state.update_data(warnings=selected["text"][lang], warnings_custom=False)
        await state.set_state(BookingStates.choosing_date)
        await message.answer(
            TEXTS[lang]["choose_date"],
            reply_markup=get_date_keyboard(lang),
        )
        return

    if message.text == TEXTS[lang]["custom_input"]:
        await state.update_data(warnings_custom=True)
        await message.answer(TEXTS[lang]["enter_warnings"])
        return

    if message.text == TEXTS[lang]["none"]:
        await state.update_data(warnings=TEXTS[lang]["none"], warnings_custom=False)
        await state.set_state(BookingStates.choosing_date)
        await message.answer(
            TEXTS[lang]["choose_date"],
            reply_markup=get_date_keyboard(lang),
        )
        return

    if data.get("warnings_custom"):
        await state.update_data(warnings=message.text.strip(), warnings_custom=False)
        await state.set_state(BookingStates.choosing_date)
        await message.answer(
            TEXTS[lang]["choose_date"],
            reply_markup=get_date_keyboard(lang),
        )
        return

    await message.answer(
        TEXTS[lang]["invalid_choice"],
        reply_markup=get_warnings_keyboard(lang),
    )


@router.message(BookingStates.choosing_date, F.text)
async def choose_date(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data["lang"]

    if message.text == TEXTS[lang]["enter_manually"]:
        await state.update_data(date_manual=True)
        await message.answer(TEXTS[lang]["enter_date_manually"])
        return

    if data.get("date_manual"):
        parsed_date = parse_manual_date(message.text)
        if not parsed_date:
            await message.answer(TEXTS[lang]["invalid_date"])
            return
        parsed_date_value = datetime.strptime(parsed_date, "%d.%m.%Y").date()
        if parsed_date_value < date.today():
            await message.answer(TEXTS[lang]["date_unavailable"])
            return
        if parsed_date_value.weekday() >= 5:
            await message.answer(TEXTS[lang]["weekend_unavailable"])
            return
        await state.update_data(date=parsed_date, date_manual=False)
        await state.set_state(BookingStates.choosing_time)
        await message.answer(
            TEXTS[lang]["choose_time"],
            reply_markup=get_time_keyboard(),
        )
        return

    normalized_text = normalize_date_button_text(message.text)
    parsed_date = parse_manual_date(normalized_text)
    if parsed_date:
        parsed_date_value = datetime.strptime(parsed_date, "%d.%m.%Y").date()
        if parsed_date_value < date.today():
            await message.answer(
                TEXTS[lang]["date_unavailable"],
                reply_markup=get_date_keyboard(lang),
            )
            return
        if parsed_date_value.weekday() >= 5:
            await message.answer(
                TEXTS[lang]["weekend_unavailable"],
                reply_markup=get_date_keyboard(lang),
            )
            return
        await state.update_data(date=parsed_date, date_manual=False)
        await state.set_state(BookingStates.choosing_time)
        await message.answer(
            TEXTS[lang]["choose_time"],
            reply_markup=get_time_keyboard(),
        )
        return

    await message.answer(
        TEXTS[lang]["invalid_choice"],
        reply_markup=get_date_keyboard(lang),
    )


@router.message(BookingStates.choosing_time, F.text.in_(TIME_SLOTS))
async def choose_time(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(time=message.text)
    await state.set_state(BookingStates.confirming)
    summary = await build_summary({**data, "time": message.text})
    await message.answer(
        summary,
        reply_markup=get_confirmation_keyboard(data["lang"]),
    )


@router.message(BookingStates.choosing_time)
async def invalid_time(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data["lang"]
    await message.answer(
        TEXTS[lang]["invalid_choice"],
        reply_markup=get_time_keyboard(),
    )


@router.message(BookingStates.confirming, F.text)
async def confirm_booking(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data["lang"]

    if message.text == TEXTS[lang]["edit"]:
        await state.set_state(BookingStates.choosing_service)
        await message.answer(
            TEXTS[lang]["booking_restart"],
            reply_markup=get_services_keyboard(lang),
        )
        return

    if message.text != TEXTS[lang]["confirm"]:
        await message.answer(
            TEXTS[lang]["invalid_choice"],
            reply_markup=get_confirmation_keyboard(lang),
        )
        return

    admin_message = build_admin_message(data, message)
    await message.bot.send_message(ADMIN_ID, admin_message)
    await message.bot.send_message(
        message.from_user.id,
        f"{TEXTS[lang]['booking_created_test']}\n\n{admin_message}",
    )
    await message.answer(
        f"{TEXTS[lang]['booking_created']}\n\n{TEXTS[lang]['booking_created_user']}\n\n/start",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()


@router.message()
async def fallback_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang")
    if lang:
        await message.answer(
            TEXTS[lang]["main_menu_prompt"],
            reply_markup=get_main_menu_keyboard(lang),
        )
        return
    await message.answer(TEXTS["en"]["missing_language"])
