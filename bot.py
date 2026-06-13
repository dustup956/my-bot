import os
import sys

import requests
from telegram import Bot
from telegram.ext import Application, CommandHandler
import asyncio

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
YOUR_CHANNEL_ID = int(os.environ.get("TELEGRAM_CHANNEL_ID", "0"))

EMOJI_MAP = {
    "carrot": "🥕", "tomato": "🍅", "strawberry": "🍓", "blueberry": "🫐",
    "corn": "🌽", "bamboo": "🎋", "pumpkin": "🎃", "apple": "🍎",
    "banana": "🍌", "mango": "🥭", "dragon": "🐉", "pineapple": "🍍",
    "grape": "🍇", "mushroom": "🍄", "cactus": "🌵", "cherry": "🍒",
    "sunflower": "🌻", "tulip": "🌷", "coconut": "🥥", "acorn": "🌰",
    "pomegranate": "🍑", "venus": "🌿", "poison": "☠️", "moon": "🌸",
    "green bean": "🫘", "bean": "🫘", "dragon's breath": "🔥",
    "watering": "🚿", "sprinkler": "💦", "trowel": "⛏️", "lantern": "🏮",
    "wheelbarrow": "🛻", "gnome": "🗿", "teleporter": "🔵", "sign": "🪧",
    "ladder": "🪜", "bench": "🪑", "light": "💡", "arch": "🏛️",
    "bridge": "🌉", "fence": "🚧", "bear trap": "🪤",
    "invisibility": "👻", "speed": "⚡", "jump": "🦘", "shrink": "🔽",
    "supersize": "🔼", "flashbang": "💥", "pot": "🪴",
}

RARITY_EMOJI = {
    "common":    "🟢",
    "uncommon":  "🔵",
    "rare":      "⭐",
    "epic":      "🔥",
    "legendary": "🌟",
    "mythic":    "💎",
    "super":     "🔮",
}

ALERT_RARITY = ["legendary", "mythic", "super"]

def get_emoji(name):
    lower = name.lower()
    for key, em in EMOJI_MAP.items():
        if key in lower:
            return em
    return "🌱"

def get_rarity_emoji(rarity):
    r = rarity.lower()
    emoji = RARITY_EMOJI.get(r, "🟢")
    is_alert = r in ALERT_RARITY
    return emoji, is_alert

def get_stock():
    try:
        r = requests.get("https://grow-a-garden-2-tracker.onrender.com/api/stock", timeout=15)
        r.raise_for_status()
        data = r.json()
        shops = data.get("shops", {})

        msg = "🌱 **Grow a Garden 2 — Актуальный сток** 🌱\n"
        has_alert = False
        all_alert_names = []

        sections = [
            ("SeedShop_Normal", "🌱 **SEEDS**"),
            ("GearShop",        "⚙️ **GEAR**"),
            ("CrateShop",       "📦 **CRATES**"),
        ]

        for shop_key, title in sections:
            items = shops.get(shop_key, [])
            in_stock = [i for i in items if i.get("stock", 0) > 0]
            if not in_stock:
                continue

            section_text = f"\n{title}\n"
            for item in in_stock:
                name = item.get("name", "")
                qty = item.get("stock", 0)
                price = item.get("price", "?")
                rarity = item.get("rarity", "Common")

                item_emoji = get_emoji(name)
                rarity_emoji, is_alert = get_rarity_emoji(rarity)

                if is_alert and shop_key == "SeedShop_Normal":
                    has_alert = True
                    all_alert_names.append(name)

                section_text += f"{rarity_emoji} {item_emoji} **{name}** | x{qty} | 💰{price} | {rarity}\n"

            msg += section_text

        return msg[:4000], has_alert, ", ".join(all_alert_names)

    except Exception as e:
        print(f"Stock fetch error: {e}")
        return "❌ Не удалось получить данные. Попробуйте позже.", False, ""

async def send_stock(bot):
    message, has_alert, alert_names = get_stock()
    if has_alert:
        header = f"🚨 **{alert_names} В МАГАЗИНЕ!** 🚨\n@everyone\n\n"
        await bot.send_message(chat_id=YOUR_CHANNEL_ID, text=header + message, parse_mode='Markdown', disable_notification=False)
    else:
        await bot.send_message(chat_id=YOUR_CHANNEL_ID, text=message, parse_mode='Markdown', disable_notification=True)
    print("✅ Сток отправлен")

async def stock_loop(bot):
    import time
    while True:
        await send_stock(bot)
        now = time.time()
        next_restock = (int(now) // 300 + 1) * 300
        wait = next_restock - now + 2
        print(f"⏳ Следующий сток через {int(wait)} сек.")
        await asyncio.sleep(wait)

async def start_cmd(update, context):
    await update.message.reply_text("✅ Бот работает!")

async def main():
    if not TOKEN:
        sys.exit("TELEGRAM_BOT_TOKEN environment variable is not set")
    if not YOUR_CHANNEL_ID:
        sys.exit("TELEGRAM_CHANNEL_ID environment variable is not set")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))

    async with app:
        await app.start()
        await app.updater.start_polling()
        print("Бот запущен...")
        await stock_loop(app.bot)

if __name__ == '__main__':
    asyncio.run(main())