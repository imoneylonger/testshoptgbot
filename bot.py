"""
🛍️ Telegram Shop Bot — Интернет-магазин
Технологии: Python 3.10+, python-telegram-bot 20.x
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from data import CATEGORIES, PRODUCTS, SHOP_NAME, ADMIN_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── ХЕЛПЕРЫ ────────────────────────────────────────────────────────────────

def get_cart(context):
    if "cart" not in context.user_data:
        context.user_data["cart"] = {}
    return context.user_data["cart"]

def cart_total(cart):
    return sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items() if pid in PRODUCTS)

def cart_text(cart):
    if not cart:
        return "Корзина пуста 🛒"
    lines = []
    for pid, qty in cart.items():
        p = PRODUCTS[pid]
        lines.append(f"• {p['name']} × {qty} = {p['price'] * qty} ₽")
    lines.append(f"\n💰 Итого: {cart_total(cart):.0f} ₽")
    return "\n".join(lines)

# ─── ГЛАВНОЕ МЕНЮ ───────────────────────────────────────────────────────────

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🛍️ Каталог", callback_data="catalog")],
        [InlineKeyboardButton("🛒 Корзина", callback_data="cart"),
         InlineKeyboardButton("📞 Контакты", callback_data="contacts")],
    ]
    await update.message.reply_text(
        f"Добро пожаловать в {SHOP_NAME}! 👋\n\nВыберите раздел:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def main_menu(update, context):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛍️ Каталог", callback_data="catalog")],
        [InlineKeyboardButton("🛒 Корзина", callback_data="cart"),
         InlineKeyboardButton("📞 Контакты", callback_data="contacts")],
    ]
    await query.edit_message_text(
        f"Главное меню {SHOP_NAME} 🏠",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ─── КАТАЛОГ ────────────────────────────────────────────────────────────────

async def show_catalog(update, context):
    query = update.callback_query
    await query.answer()
    buttons = [
        [InlineKeyboardButton(cat["emoji"] + " " + cat["name"], callback_data=f"cat_{cid}")]
        for cid, cat in CATEGORIES.items()
    ]
    buttons.append([InlineKeyboardButton("🏠 Главная", callback_data="main")])
    await query.edit_message_text(
        "📦 Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_category(update, context):
    query = update.callback_query
    await query.answer()
    cat_id = query.data.split("_", 1)[1]
    cat = CATEGORIES.get(cat_id)
    if not cat:
        await query.edit_message_text("Категория не найдена.")
        return
    items = [(pid, p) for pid, p in PRODUCTS.items() if p["category"] == cat_id]
    buttons = [
        [InlineKeyboardButton(f"{p['name']} — {p['price']} ₽", callback_data=f"prod_{pid}")]
        for pid, p in items
    ]
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="catalog")])
    await query.edit_message_text(
        f"{cat['emoji']} {cat['name']}\n\nВыберите товар:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_product(update, context):
    query = update.callback_query
    await query.answer()
    pid = query.data.split("_", 1)[1]
    p = PRODUCTS.get(pid)
    if not p:
        await query.edit_message_text("Товар не найден.")
        return
    cart = get_cart(context)
    qty = cart.get(pid, 0)
    text = (
        f"*{p['name']}*\n\n"
        f"{p['description']}\n\n"
        f"💰 Цена: *{p['price']} ₽*\n"
        f"📦 В корзине: {qty} шт."
    )
    buttons = [[InlineKeyboardButton("➕ Добавить в корзину", callback_data=f"add_{pid}")]]
    if qty > 0:
        buttons.append([InlineKeyboardButton(f"➖ Убрать ({qty} шт.)", callback_data=f"remove_{pid}")])
    buttons.append([
        InlineKeyboardButton("◀️ Назад", callback_data=f"cat_{p['category']}"),
        InlineKeyboardButton("🛒 Корзина", callback_data="cart"),
    ])
    if p.get("photo"):
        try:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=p["photo"],
                caption=text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
        except Exception:
            pass
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))

# ─── КОРЗИНА ────────────────────────────────────────────────────────────────

async def add_to_cart(update, context):
    query = update.callback_query
    await query.answer("✅ Добавлено в корзину!")
    pid = query.data.split("_", 1)[1]
    cart = get_cart(context)
    cart[pid] = cart.get(pid, 0) + 1
    await show_product(update, context)

async def remove_from_cart(update, context):
    query = update.callback_query
    pid = query.data.split("_", 1)[1]
    cart = get_cart(context)
    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            del cart[pid]
    await query.answer("➖ Убрано из корзины")
    await show_product(update, context)

async def show_cart(update, context):
    query = update.callback_query
    await query.answer()
    cart = get_cart(context)
    buttons = []
    if cart:
        buttons.append([InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")])
        buttons.append([InlineKeyboardButton("🗑️ Очистить корзину", callback_data="clear_cart")])
    buttons.append([
        InlineKeyboardButton("🛍️ В каталог", callback_data="catalog"),
        InlineKeyboardButton("🏠 Главная", callback_data="main"),
    ])
    await query.edit_message_text(
        f"🛒 *Ваша корзина:*\n\n{cart_text(cart)}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def clear_cart(update, context):
    query = update.callback_query
    context.user_data["cart"] = {}
    await query.answer("🗑️ Корзина очищена")
    await show_cart(update, context)

# ─── ОФОРМЛЕНИЕ ЗАКАЗА ──────────────────────────────────────────────────────

async def checkout(update, context):
    query = update.callback_query
    await query.answer()
    cart = get_cart(context)
    if not cart:
        await query.edit_message_text("Корзина пуста. Добавьте товары!")
        return
    context.user_data["awaiting_name"] = True
    await query.edit_message_text(
        "📝 Введите ваше *имя и номер телефона*:\n\n"
        "Пример: _Иван Иванов, +7 999 123 45 67_",
        parse_mode="Markdown"
    )

async def handle_order_info(update, context):
    if not context.user_data.get("awaiting_name"):
        return
    context.user_data["awaiting_name"] = False
    cart = get_cart(context)
    user = update.effective_user
    contact_info = update.message.text
    order_text = (
        f"🛍️ *Новый заказ!*\n\n"
        f"👤 Клиент: {user.full_name} (@{user.username or 'нет'})\n"
        f"📞 Контакт: {contact_info}\n\n"
        f"📦 *Состав заказа:*\n{cart_text(cart)}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=order_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Не удалось отправить заказ: {e}")
    context.user_data["cart"] = {}
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main")]]
    await update.message.reply_text(
        "✅ *Заказ принят!* Мы свяжемся с вами в ближайшее время.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ─── КОНТАКТЫ ───────────────────────────────────────────────────────────────

async def show_contacts(update, context):
    query = update.callback_query
    await query.answer()
    buttons = [[InlineKeyboardButton("🏠 Главная", callback_data="main")]]
    await query.edit_message_text(
        "📞 *Контакты:*\n\n"
        "📱 Телефон: +7 999 000 00 00\n"
        "📧 Email: shop@example.com\n"
        "🕐 Режим работы: Пн–Пт 9:00–18:00",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ─── ЗАПУСК ─────────────────────────────────────────────────────────────────

def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("Установи переменную BOT_TOKEN!")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(main_menu,        pattern="^main$"))
    app.add_handler(CallbackQueryHandler(show_catalog,     pattern="^catalog$"))
    app.add_handler(CallbackQueryHandler(show_category,    pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(show_product,     pattern="^prod_"))
    app.add_handler(CallbackQueryHandler(add_to_cart,      pattern="^add_"))
    app.add_handler(CallbackQueryHandler(remove_from_cart, pattern="^remove_"))
    app.add_handler(CallbackQueryHandler(show_cart,        pattern="^cart$"))
    app.add_handler(CallbackQueryHandler(clear_cart,       pattern="^clear_cart$"))
    app.add_handler(CallbackQueryHandler(checkout,         pattern="^checkout$"))
    app.add_handler(CallbackQueryHandler(show_contacts,    pattern="^contacts$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_info))

    logger.info("Бот запущен ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
