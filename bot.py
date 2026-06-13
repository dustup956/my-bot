import logging
import os
import time

import requests
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler
import asyncio

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8934098702:AAGU4a-elfGLbbXH1h8jqABBFDWmLhtlnFY")
YOUR_CHANNEL_ID = -1004305027195

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

    except requests.RequestException as e:
        logger.exception("Network error while fetching stock data")
        return f"❌ Ошибка сети: {e}", False, ""
    except (KeyError, ValueError, TypeError) as e:
        logger.exception("Failed to parse stock API response")
        return f"❌ Ошибка обработки данных: {e}", False, ""

async def send_stock(bot):
    message, has_alert, alert_names = get_stock()
    try:
        if has_alert:
            header = f"🚨 **{alert_names} В МАГАЗИНЕ!** 🚨\n@everyone\n\n"
            await bot.send_message(chat_id=YOUR_CHANNEL_ID, text=header + message, parse_mode='Markdown', disable_notification=False)
        else:
            await bot.send_message(chat_id=YOUR_CHANNEL_ID, text=message, parse_mode='Markdown', disable_notification=True)
    except TelegramError as e:
        logger.error("Failed to send stock message to Telegram: %s", e)
        raise
    logger.info("Сток отправлен")

async def stock_loop(bot):
    consecutive_failures = 0
    while True:
        try:
            await send_stock(bot)
            consecutive_failures = 0
        except TelegramError:
            consecutive_failures += 1
            backoff = min(60 * consecutive_failures, 300)
            logger.warning(
                "Stock update failed (%d consecutive). Retrying in %ds.",
                consecutive_failures, backoff,
            )
            await asyncio.sleep(backoff)
            continue
        except Exception:
            consecutive_failures += 1
            logger.exception("Unexpected error in stock loop (attempt %d)", consecutive_failures)
            await asyncio.sleep(30)
            continue

        now = time.time()
        next_restock = (int(now) // 300 + 1) * 300
        wait = next_restock - now + 2
        logger.info("Следующий сток через %d сек.", int(wait))
        await asyncio.sleep(wait)

async def start_cmd(update, context):
    try:
        await update.message.reply_text("✅ Бот работает!")
    except TelegramError as e:
        logger.error("Failed to reply to /start command: %s", e)

async def main():
    if not TOKEN:
        logger.critical("TELEGRAM_BOT_TOKEN is not set")
        return

    try:
        app = Application.builder().token(TOKEN).build()
    except Exception:
        logger.exception("Failed to build Telegram application")
        return

    app.add_handler(CommandHandler("start", start_cmd))

    async with app:
        await app.start()
        await app.updater.start_polling()
        logger.info("Бот запущен")
        await stock_loop(app.bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception:
        logger.exception("Fatal error")