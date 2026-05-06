# 🍦 Mazza Muzqaymoq - Telegram Bot

Telegram bot orqali muzqaymoq buyurtmalari uchun.

## 🚀 Railway'ga joyish

### 1. Repository'ni tayyorlash
```bash
git clone https://github.com/saloxiddinkomilov2-design/Mazzaice.git
cd Mazzaice
```

### 2. Railway'ga ulash
- https://railway.app ga o'ting
- GitHub akkauntingiz bilan kiriting
- "New Project" → "Deploy from GitHub" tanlang
- Bu repository'ni tanlang

### 3. Environment Variables o'rnatish
Railway'ning project sozlamalarida quyidagi variables ni qo'shing:

```
BOT_TOKEN=your_telegram_bot_token_here
OWNER_ID=your_telegram_id_here
```

**Bot tokenini qanday olish:**
1. Telegramda `@BotFather` ga xabar yuboring
2. `/newbot` buyrug'i kiriting
3. Bot nomi va username ni kiriting
4. Hosil bo'lgan tokenni `.env` fayliga qo'ying

**OWNER_ID ni qanday topish:**
1. Telegramda `@userinfobot` ga xabar yuboring
2. O'z ID'ingizni ko'ring va `.env` fayliga qo'ying

### 4. Deploy qilish
Railway avtomatik ravishda kod o'zgartirganda deploy qiladi.

## 📁 Fayllar tuzilishi

```
Mazzaice/
├── main.py           # Asosiy bot kodi
├── requirements.txt  # Python kutubxonalari
├── Procfile         # Railway'ga qanday ishlatishni aytish
├── .env.example     # Environment variables misoli
├── .gitignore       # Git'dan e'tiborga olmaydigan fayllar
└── README.md        # Bu fayl
```

## 📋 Bot funksiyalari

- ✅ Buyurtma berish jarayoni (Multi-step conversation)
- ✅ Menyu ko'rish
- ✅ Aloqa ma'lumotlarini ko'rish
- ✅ Egaga buyurtma haqida xabar yuborish
- ✅ Telefon raqamini turli usullar bilan qabul qilish

## 🔒 Xavfsizlik

⚠️ **Muhim**: Bot tokenini hech qachon GitHub'ga commit qilmang!
- `.env` fayl `.gitignore` da yashiringan
- Token Environment Variables orqali Railway'da saqlanadi

## 🛠️ Local'da test qilish

```bash
# Virtual environment yaratish
python3 -m venv venv
source venv/bin/activate

# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# .env faylini tayyorlash
cp .env.example .env
# .env faylini o'z token va ID bilan to'ldiring

# Botni ishga tushirish
python main.py
```

## 📞 Support

Agar muammo bo'lsa:
1. Railway logs'larini tekshiring
2. `.env` faylining to'g'ri ekanligini tekshiring
3. Bot tokenini tekshiring (@BotFather'dan yangi token oling)

---

**Mazza Bot v1.0** 🍦
