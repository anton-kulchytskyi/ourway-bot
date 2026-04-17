from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/today"),
                KeyboardButton(text="/my"),
                KeyboardButton(text="/add"),
            ],
            [
                KeyboardButton(text="/tonight"),
                KeyboardButton(text="/schedule"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose a command...",
    )
