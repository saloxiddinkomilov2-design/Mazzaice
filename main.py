#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🍦 MAZZA MUZQAYMOQ - Telegram Bot
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

if not BOT_TOKEN or OWNER_ID == 0:
    raise ValueError("❌ BOT_TOKEN yoki OWNER_ID topilmadi! .env faylni tekshiring.")

NAME, PHONE, PRODUCT, QTY, MORE, CONFIRM = range(6)

# Menyu — emoji YO'Q, faqat sof matn (Telegram tugma matni bilan mos keladi)
MENU = {
    "Yumshoq Muzqaymoq (kg)": 40000,
    "Katta idish 0.7kg":      30000,
    "Idish 0.5kg":            20000,
    "Idish 0.4L":             15000,
    "Idish 0.3L":             10000,
    "Idish 0.2L":              5000,
    "Rojok Katta":             5000,
    "Fakel Kichkina":          3000,
    "Gazli Suv 250ml":         2000,
    "Gazli Suv 500ml":         4000,
    "Gazli Suv 1 litr":        7000,
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def find_menu_key(text: str):
    """strip() + lower() bilan xavfsiz qidirish — IDISH muammosini hal qiladi."""
    if not text:
        return None
    cleaned = text.strip().lower()
    for key in MENU:
        if key.strip().lower() == cleaned:
            return key
    return None


def product_keyboard():
    rows = [[key] for key in MENU.keys()]
    rows.append(["❌ Bekor qilish"])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def cart_text(cart: list) -> str:
    if not cart:
        return "Savatcha bo'sh"
    lines = []
    total = 0
    for i, item in enumerate(cart, 1):
        sub = item["price"] * item["qty"]
        total += sub
        lines.append(f"{i}. {item['product']} x{item['qty']} = {sub:,} so'm")
    lines.append(f"\nJami: {total:,} so'm")
    return "\n".join(lines)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    user = update.effective_user
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}! 👋\n\n"
        f"🍦 *Mazza Muzqaymoq* botiga xush kelibsiz!\n\n"
        f"Buyurtma berish uchun quyidagi tugmani bosing 👇",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["🍦 Buyurtma berish"], ["📋 Menyu", "📞 Aloqa"]],
            resize_keyboard=True
        )
    )


async def show_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = "📋 *Bizning Menyu:*\n\n"
    for key, price in MENU.items():
        text += f"• {key} — *{price:,} so'm*\n"
    text += "\n📍 Farg'ona vil., Qo'shtepa tumani"
    await update.message.reply_text(text, parse_mode="Markdown")


async def contact_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *Aloqa:*\n\n"
        "📱 Telefon: +998 91 107 19 96\n"
        "📍 Manzil: Farg'ona vil., Qo'shtepa tumani\n"
        "🕐 Ish vaqti: 09:00 – 22:00",
        parse_mode="Markdown"
    )


async def order_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["cart"] = []
    await update.message.reply_text(
        "🛒 *Buyurtma berish boshlandi!*\n\n"
        "1️⃣ Ismingizni yozing:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["❌ Bekor qilish"]], resize_keyboard=True
        )
    )
    return NAME


async def get_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Bekor qilish":
        return await cancel(update, ctx)
    ctx.user_data["name"] = update.message.text.strip()
    phone_btn = KeyboardButton("📱 Raqamni yuborish", request_contact=True)
    await update.message.reply_text(
        f"✅ Ism: *{ctx.user_data['name']}*\n\n"
        f"2️⃣ Telefon raqamingizni yuboring:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [[phone_btn], ["❌ Bekor qilish"]], resize_keyboard=True
        )
    )
    return PHONE


async def get_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text == "❌ Bekor qilish":
        return await cancel(update, ctx)
    if update.message.contact:
        phone = update.message.contact.phone_number
    elif update.message.text:
        phone = update.message.text.strip()
    else:
        await update.message.reply_text("⚠️ Telefon raqamini yuboring!")
        return PHONE
    ctx.user_data["phone"] = phone
    await update.message.reply_text(
        f"✅ Telefon: *{phone}*\n\n"
        f"3️⃣ Mahsulot tanlang:",
        parse_mode="Markdown",
        reply_markup=product_keyboard()
    )
    return PRODUCT


async def get_product(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Bekor qilish":
        return await cancel(update, ctx)

    key = find_menu_key(text)  # ← BU YERDA MUAMMO HAL BO'LADI
    if key is None:
        await update.message.reply_text(
            "⚠️ Iltimos, ro'yxatdan mahsulot tanlang!",
            reply_markup=product_keyboard()
        )
        return PRODUCT

    ctx.user_data["current_product"] = key
    ctx.user_data["current_price"] = MENU[key]

    await update.message.reply_text(
        f"✅ Tanlandi: *{key}*\n"
        f"💰 Narx: *{MENU[key]:,} so'm*\n\n"
        f"4️⃣ Nechta kerak?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["1", "2", "3"], ["4", "5", "10"], ["❌ Bekor qilish"]],
            resize_keyboard=True
        )
    )
    return QTY


async def get_qty(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Bekor qilish":
        return await cancel(update, ctx)
    try:
        qty = int(update.message.text.strip())
        if qty < 1:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ Iltimos, musbat raqam kiriting!")
        return QTY

    product = ctx.user_data["current_product"]
    price = ctx.user_data["current_price"]
    cart = ctx.user_data["cart"]

    for item in cart:
        if item["product"] == product:
            item["qty"] += qty
            break
    else:
        cart.append({"product": product, "price": price, "qty": qty})

    await update.message.reply_text(
        f"✅ Savatchaga qo'shildi!\n\n"
        f"🛒 *Savatchangiz:*\n{cart_text(cart)}\n\n"
        f"Yana mahsulot qo'shasizmi?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["➕ Yana mahsulot qo'shish"], ["✅ Buyurtmani tasdiqlash"], ["❌ Bekor qilish"]],
            resize_keyboard=True
        )
    )
    return MORE


async def more_or_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Bekor qilish":
        return await cancel(update, ctx)

    if text == "➕ Yana mahsulot qo'shish":
        await update.message.reply_text(
            "Mahsulot tanlang:",
            reply_markup=product_keyboard()
        )
        return PRODUCT

    if text == "✅ Buyurtmani tasdiqlash":
        cart = ctx.user_data["cart"]
        total = sum(i["price"] * i["qty"] for i in cart)
        summary = (
            f"📋 *Buyurtma ma'lumotlari:*\n\n"
            f"👤 Ism: {ctx.user_data['name']}\n"
            f"📞 Telefon: {ctx.user_data['phone']}\n\n"
            f"🛒 *Mahsulotlar:*\n{cart_text(cart)}\n\n"
            f"✅ Tasdiqlaysizmi?"
        )
        await update.message.reply_text(
            summary, parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [["✅ Tasdiqlash"], ["❌ Bekor qilish"]], resize_keyboard=True
            )
        )
        return CONFIRM

    await update.message.reply_text(
        "⚠️ Tugmalardan birini tanlang.",
        reply_markup=ReplyKeyboardMarkup(
            [["➕ Yana mahsulot qo'shish"], ["✅ Buyurtmani tasdiqlash"], ["❌ Bekor qilish"]],
            resize_keyboard=True
        )
    )
    return MORE


async def confirm_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Bekor qilish":
        return await cancel(update, ctx)
    if update.message.text != "✅ Tasdiqlash":
        return CONFIRM

    d = ctx.user_data
    cart = d["cart"]
    user = update.effective_user
    total = sum(i["price"] * i["qty"] for i in cart)

    items_text = ""
    for item in cart:
        items_text += f"  • {item['product']} x{item['qty']} = {item['price']*item['qty']:,} so'm\n"

    username = f"@{user.username}" if user.username else "yo'q"
    owner_msg = (
        f"🔔 *YANGI BUYURTMA!*\n\n"
        f"👤 Ism: {d['name']}\n"
        f"📞 Telefon: {d['phone']}\n\n"
        f"🛒 Mahsulotlar:\n{items_text}\n"
        f"💰 *Jami: {total:,} so'm*\n\n"
        f"💳 Karta: `9860030367057004`\n\n"
        f"📱 Telegram: {username}\n"
        f"🆔 User ID: {user.id}"
    )

    try:
        await ctx.bot.send_message(chat_id=OWNER_ID, text=owner_msg, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Egaga xabar yuborishda xato: {e}")

    await update.message.reply_text(
        f"🎉 *Buyurtmangiz qabul qilindi!*\n\n"
        f"Tez orada siz bilan bog'lanamiz.\n"
        f"📞 +998 91 107 19 96\n\n"
        f"💳 *To'lov uchun karta raqami:*\n"
        f"`9860030367057004`\n\n"
        f"Rahmat! Mazza ni tanlaguningiz uchun 🍦",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["🍦 Buyurtma berish"], ["📋 Menyu", "📞 Aloqa"]], resize_keyboard=True
        )
    )
    ctx.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text(
        "❌ Buyurtma bekor qilindi.\n\nQaytadan boshlash uchun tugmani bosing.",
        reply_markup=ReplyKeyboardMarkup(
            [["🍦 Buyurtma berish"], ["📋 Menyu", "📞 Aloqa"]], resize_keyboard=True
        )
    )
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🍦 Buyurtma berish$"), order_start)
        ],
        states={
            NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE:   [MessageHandler((filters.TEXT | filters.CONTACT) & ~filters.COMMAND, get_phone)],
            PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product)],
            QTY:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_qty)],
            MORE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, more_or_confirm)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^📋 Menyu$"), show_menu))
    app.add_handler(MessageHandler(filters.Regex("^📞 Aloqa$"), contact_info))
    app.add_handler(conv)

    print("🍦 Mazza bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
