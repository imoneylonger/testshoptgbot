"""
📦 Данные магазина — редактируй под каждого клиента!
"""

import os

# ─── НАСТРОЙКИ МАГАЗИНА ─────────────────────────────────────────────────────

SHOP_NAME = "Test Shop"          # Название магазина
ADMIN_ID = int(os.getenv("ADMIN_ID", "771970081"))  # Твой Telegram ID

# ─── КАТЕГОРИИ ──────────────────────────────────────────────────────────────
# Формат: "id_категории": {"name": "Название", "emoji": "🔥"}

CATEGORIES = {
    "electronics": {"name": "Электроника",    "emoji": "📱"},
    "clothing":    {"name": "Одежда",         "emoji": "👕"},
    "home":        {"name": "Для дома",       "emoji": "🏠"},
}

# ─── ТОВАРЫ ─────────────────────────────────────────────────────────────────
# Формат: "id_товара": {поля товара}
# photo: ссылка на фото (URL) или None

PRODUCTS = {
    "iphone15": {
        "name":        "iPhone 15 128GB",
        "description": "Смартфон Apple iPhone 15, 128 ГБ. Цвет: чёрный. Гарантия 1 год.",
        "price":       79990,
        "category":    "electronics",
        "photo":       None,
    },
    "airpods": {
        "name":        "AirPods Pro 2",
        "description": "Беспроводные наушники с активным шумоподавлением. Кейс MagSafe.",
        "price":       19990,
        "category":    "electronics",
        "photo":       None,
    },
    "tshirt_basic": {
        "name":        "Футболка оверсайз",
        "description": "100% хлопок, плотность 240 г/м². Размеры: S, M, L, XL. Цвет: белый/чёрный.",
        "price":       1990,
        "category":    "clothing",
        "photo":       None,
    },
    "hoodie": {
        "name":        "Худи premium",
        "description": "Тёплое худи с начёсом, 80% хлопок, 20% полиэстер. Унисекс.",
        "price":       3990,
        "category":    "clothing",
        "photo":       None,
    },
    "lamp": {
        "name":        "Умная лампа Xiaomi",
        "description": "LED лампа с управлением через приложение. 16 млн цветов, 800 люмен.",
        "price":       1490,
        "category":    "home",
        "photo":       None,
    },
    "mug": {
        "name":        "Термокружка 500 мл",
        "description": "Нержавеющая сталь. Держит тепло до 8 часов. Крышка-защита от проливания.",
        "price":       890,
        "category":    "home",
        "photo":       None,
    },
}

