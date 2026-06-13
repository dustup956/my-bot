import asyncio
import time

from telegram.ext import Application, CommandHandler

from config import CHANNEL_ID, RESTOCK_BUFFER, RESTOCK_INTERVAL, TOKEN
from utils import fetch_stock


async def send_stock(bot):
    message, has_alert, alert_names = fetch_stock()
    if has_alert:
        header = f"\U0001f6a8 **{alert_names} \u0412 \u041c\u0410\u0413\u0410\u0417\u0418\u041d\u0415!** \U0001f6a8\n@everyone\n\n"
        message = header + message

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode="Markdown",
        disable_notification=not has_alert,
    )
    print("\u2705 \u0421\u0442\u043e\u043a \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d")


async def stock_loop(bot):
    while True:
        await send_stock(bot)
        now = time.time()
        next_restock = (int(now) // RESTOCK_INTERVAL + 1) * RESTOCK_INTERVAL
        wait = next_restock - now + RESTOCK_BUFFER
        print(f"\u23f3 \u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u0441\u0442\u043e\u043a \u0447\u0435\u0440\u0435\u0437 {int(wait)} \u0441\u0435\u043a.")
        await asyncio.sleep(wait)


async def start_cmd(update, context):
    await update.message.reply_text("\u2705 \u0411\u043e\u0442 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442!")


async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))

    async with app:
        await app.start()
        await app.updater.start_polling()
        print("\u0411\u043e\u0442 \u0437\u0430\u043f\u0443\u0449\u0435\u043d...")
        await stock_loop(app.bot)


if __name__ == "__main__":
    asyncio.run(main())
