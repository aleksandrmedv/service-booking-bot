from datetime import date, timedelta

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from data import PREFERENCES, SERVICES, TIME_SLOTS, WARNINGS
from utils.texts import LANGUAGE_LABELS, TEXTS


def build_keyboard(rows: list[list[str]], resize: bool = True) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text) for text in row]
            for row in rows
        ],
        resize_keyboard=resize,
    )


def get_language_keyboard() -> ReplyKeyboardMarkup:
    return build_keyboard(
        [
            [LANGUAGE_LABELS["ru"], LANGUAGE_LABELS["en"], LANGUAGE_LABELS["se"]],
        ]
    )


def get_main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return build_keyboard(
        [
            [TEXTS[lang]["services"]],
            [TEXTS[lang]["address"], TEXTS[lang]["contact"]],
        ]
    )


def get_services_keyboard(lang: str) -> ReplyKeyboardMarkup:
    rows = [
        [TEXTS[lang]["service_with_price"].format(name=service["name"][lang], price=service["price"])]
        for service in SERVICES
    ]
    rows.append([TEXTS[lang]["address"], TEXTS[lang]["contact"]])
    return build_keyboard(rows)
def get_preferences_keyboard(lang: str) -> ReplyKeyboardMarkup:
    rows = [[item["text"][lang]] for item in PREFERENCES]
    rows.append([TEXTS[lang]["custom_input"], TEXTS[lang]["skip"]])
    return build_keyboard(rows)


def get_warnings_keyboard(lang: str) -> ReplyKeyboardMarkup:
    rows = [[item["text"][lang]] for item in WARNINGS]
    rows.append([TEXTS[lang]["custom_input"], TEXTS[lang]["none"]])
    return build_keyboard(rows)


def get_date_keyboard(lang: str) -> ReplyKeyboardMarkup:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    rows: list[list[str]] = []

    for week in range(3):
        row = []
        for day_offset in range(5):
            current = week_start + timedelta(days=week * 7 + day_offset)
            label = current.strftime("%d.%m.%y")
            if current < today:
                row.append(f"☑️ {label}")
            else:
                row.append(f"✅ {label}")
        rows.append(row)

    rows.append([TEXTS[lang]["enter_manually"]])
    return build_keyboard(rows)


def get_time_keyboard() -> ReplyKeyboardMarkup:
    rows = [[slot] for slot in TIME_SLOTS]
    return build_keyboard(rows)


def get_confirmation_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return build_keyboard(
        [
            [TEXTS[lang]["confirm"], TEXTS[lang]["edit"]],
        ]
    )
