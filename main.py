#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🍦 MAZZA MUZQAYMOQ - Telegram Bot
Mijozlar bu bot orqali buyurtma beradi,
siz esa bildirishnoma olasiz.
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

# Load environment variables
load_dotenv()

# =============================================
# SOZLAMALAR
# =============================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

if not BOT_TOKEN or not OWNER_ID:
    raise ValueError("❌ BOT_TOKEN yoki OWNER_ID topilmadi! .env faylni tekshiring.")

# =============================================
# BOSQICHLAR
# =============================================
NAME, PHONE, PRODUCT, QTY, CONFIRM = range(5)

# Menyu
MENU = {
    "🍦 Yumshoq Muzqaymoq (kg)": 40000,
    "🍦 Rojok — Katta":           5000,
    "🍦 Fakel — Kichkina":        3000,
    "🥤 Gazli Suv 250ml":         2000,
    "🥤 Gazli Suv 500ml":         4000,
    "🥤 Gazli Suv 1 litr":        7000,
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =============================================
# /start — Boshlash
# =============================================
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}! 👋\n\n"
        f"🍦 *Mazza Muzqaymoq* botiga xush kelibsiz!\n\n"
        f"Bu bot orqali siz osongina buyurtma berishingiz mumkin.\n\n"
        f"Boshlash uchun quyidagi tugmani bosing 👇",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["🍦 Buyurtma berish"], ["📋 Menyu", "📞 Aloqa"]],
            resize_keyboard=True
        )
    )

# =============================================
# Menyu ko'rish
# =============================================
async def show_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = "📋 *Bizning Menyu:*\n\n"
    for name, price in MENU.items():
        text += f"{name} — *{price:,} so'm*\n"
    text += "\n📍 Farg'ona vil., Qo'shtepa tumani"
    await update.message.reply_text(text, parse_mode="Markdown")

# =============================================
# Aloqa
# =============================================
async def contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *Aloqa:*\n\n"
        "📱 Telefon: +998 91 107 19 96\n"
        "📍 Manzil: Farg'ona vil., Qo'shtepa tumani\n"
        "🕐 Ish vaqti: 09:00 – 22:00",
        parse_mode="Markdown"
    )

# =============================================
# BUYURTMA JARAYONI
# =============================================

# 1. Ism so'rash
async def order_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 *Buyurtma berish boshlandi!*\n\n"
        "1️⃣ Ismingizni yozing:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["❌ Bekor qilish"]],
            resize_keyboard=True
        )
    )
    return NAME

# 2. Ismni saqlash, telefon so'rash
async def get_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Bekor qilish":
        return await cancel(update, ctx)

    ctx.user_data["name"] = update.message.text

    phone_btn = KeyboardButton("📱 Raqamni yuborish", request_contact=True)
    await update.message.reply_text(
        f"✅ Ism: *{ctx.user_data['name']}*\n\n"
        f"2️⃣ Telefon raqamingizni yuboring\n"
        f"(Yoki tugmani bosing):",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [[phone_btn], ["❌ Bekor qilish"]],
            resize_keyboard=True
        )
    )
    return PHONE

# 3. Telefon saqlash, mahsulot so'rash
async def get_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Bekor qilish":
        return await cancel(update, ctx)

    if update.message.contact:
        ctx.user_data["phone"] = update.message.contact.phone_number
    else:
        ctx.user_data["phone"] = update.message.text

    products = [[p] for p in MENU.keys()]
    products.append(["❌ Bekor qilish"])

    await update.message.reply_text(
        f"✅ Telefon: *{ctx.user_data['phone']}*\n\n"
        f"3️⃣ Mahsulot tanlang:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(products, resize_keyboard=True)
    )
    return PRODUCT

# 4. Mahsulot saqlash, miqdor so'rash
async def get_product(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Bekor qilish":
        return await cancel(update, ctx)

    if update.message.text not in MENU:
        await update.message.reply_text("⚠️ Iltimos, ro'yxatdan tanlang!")
        return PRODUCT

    ctx.user_data["product"] = update.message.text
    ctx.user_data["price"]   = MENU[update.message.text]

    await update.message.reply_text(
        f"✅ Mahsulot: *{ctx.user_data['product']}*\n"
        f"💰 Narx: *{ctx.user_data['price']:,} so'm*\n\n"
        f"4️⃣ Nechta kerak?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["1", "2", "3"], ["4", "5", "10"], ["❌ Bekor qilish"]],
            resize_keyboard=True
        )
    )
    return QTY

# 5. Miqdor saqlash, tasdiqlash
async def get_qty(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Bekor qilish":
        return await cancel(update, ctx)

    try:
        qty = int(update.message.text)
        if qty < 1:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ Iltimos, raqam kiriting!")
        return QTY

    ctx.user_data["qty"] = qty
    ctx.user_data["total"] = qty * ctx.user_data["price"]

    summary = (
        f"📋 *Buyurtma ma'lumotlari:*\n\n"
        f"👤 Ism: {ctx.user_data['name']}\n"
        f"📞 Telefon: {ctx.user_data['phone']}\n"
        f"🍦 Mahsulot: {ctx.user_data['product']}\n"
        f"🔢 Miqdor: {qty} ta\n"
        f"💰 Jami: *{ctx.user_data['total']:,} so'm*\n\n"
        f"✅ Tasdiqlaysizmi?"
    )

    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["✅ Tasdiqlash"], ["❌ Bekor qilish"]],
            resize_keyboard=True
        )
    )
    return CONFIRM

# 6. Tasdiqlash — buyurtmani jo'natish
async def confirm_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Bekor qilish":
        return await cancel(update, ctx)

    if update.message.text != "✅ Tasdiqlash":
        return CONFIRM

    d = ctx.user_data
    user = update.effective_user

    # Egaga xabar yuborish
    owner_msg = (
        f"🔔 *YANGI BUYURTMA!*\n\n"
        f"👤 Ism: {d['name']}\n"
        f"📞 Telefon: {d['phone']}\n"
        f"🍦 Mahsulot: {d['product']}\n"
        f"🔢 Miqdor: {d['qty']} ta\n"
        f"💰 Jami: *{d['total']:,} so'm*\n\n"
        f"📱 Telegram: @{user.username or 'noma\\'lum'}\n"
        f"🆔 User ID: {user.id}"
    )

    try:
        await ctx.bot.send_message(
            chat_id=OWNER_ID,
            text=owner_msg,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Egaga xabar yuborishda xato: {e}")

    # Mijozga tasdiqlash
    await update.message.reply_text(
        f"🎉 *Buyurtmangiz qabul qilindi!*\n\n"
        f"Tez orada siz bilan bog'lanamiz.\n"
        f"📞 +998 91 107 19 96\n\n"
        f"Rahmat! Mazza ni tanlaguningiz uchun 🍦",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [["🍦 Buyurtma berish"], ["📋 Menyu", "📞 Aloqa"]],
            resize_keyboard=True
        )
    )
    ctx.user_data.clear()
    return ConversationHandler.END

# Bekor qilish
async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text(
        "❌ Buyurtma bekor qilindi.\n\nQaytadan boshlash uchun /start bosing.",
        reply_markup=ReplyKeyboardMarkup(
            [["🍦 Buyurtma berish"], ["📋 Menyu", "📞 Aloqa"]],
            resize_keyboard=True
        )
    )
    return ConversationHandler.END

# =============================================
# MAIN
# =============================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Buyurtma jarayoni
    conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("🍦 Buyurtma berish"), order_start)
        ],
        states={
            NAME:    [MessageHandler(filters.ALL, get_name)],
            PHONE:   [MessageHandler(filters.ALL, get_phone)],
            PRODUCT: [MessageHandler(filters.ALL, get_product)],
            QTY:     [MessageHandler(filters.ALL, get_qty)],
            CONFIRM: [MessageHandler(filters.ALL, confirm_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("📋 Menyu"), show_menu))
    app.add_handler(MessageHandler(filters.Regex("📞 Aloqa"), contact))
    app.add_handler(conv)

    print("🍦 Mazza bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
