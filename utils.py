import requests

from config import (
    API_TIMEOUT,
    API_URL,
    ALERT_RARITIES,
    DEFAULT_ITEM_EMOJI,
    DEFAULT_RARITY_EMOJI,
    EMOJI_MAP,
    RARITY_EMOJI,
    SHOP_SECTIONS,
)


def lookup_emoji(name, mapping, default, substring_match=False):
    """Generic emoji lookup: exact key match or substring search."""
    key = name.lower()
    if substring_match:
        for pattern, emoji in mapping.items():
            if pattern in key:
                return emoji
        return default
    return mapping.get(key, default)


def get_item_emoji(name):
    return lookup_emoji(name, EMOJI_MAP, DEFAULT_ITEM_EMOJI, substring_match=True)


def get_rarity_emoji(rarity):
    return lookup_emoji(rarity, RARITY_EMOJI, DEFAULT_RARITY_EMOJI)


def is_alert_rarity(rarity):
    return rarity.lower() in ALERT_RARITIES


def format_item_line(item):
    """Format a single shop item into a display line."""
    name = item.get("name", "")
    qty = item.get("stock", 0)
    price = item.get("price", "?")
    rarity = item.get("rarity", "Common")

    item_emoji = get_item_emoji(name)
    rarity_emoji = get_rarity_emoji(rarity)

    return (
        f"{rarity_emoji} {item_emoji} **{name}** | x{qty} "
        f"| \U0001f4b0{price} | {rarity}\n"
    )


def format_shop_section(title, items):
    """Format an entire shop section; returns (text, alert_names)."""
    in_stock = [i for i in items if i.get("stock", 0) > 0]
    if not in_stock:
        return "", []

    alert_names = []
    section = f"\n{title}\n"
    for item in in_stock:
        section += format_item_line(item)
        rarity = item.get("rarity", "Common")
        if is_alert_rarity(rarity):
            alert_names.append(item.get("name", ""))

    return section, alert_names


def fetch_stock():
    """Fetch stock from the API and return (message, has_alert, alert_csv)."""
    try:
        r = requests.get(API_URL, timeout=API_TIMEOUT)
        r.raise_for_status()
        shops = r.json().get("shops", {})

        msg = "\U0001f331 **Grow a Garden 2 \u2014 \u0410\u043a\u0442\u0443\u0430\u043b\u044c\u043d\u044b\u0439 \u0441\u0442\u043e\u043a** \U0001f331\n"
        all_alert_names = []

        for shop_key, title in SHOP_SECTIONS:
            items = shops.get(shop_key, [])
            section_text, alerts = format_shop_section(title, items)
            msg += section_text
            if shop_key == "SeedShop_Normal":
                all_alert_names.extend(alerts)

        has_alert = bool(all_alert_names)
        return msg[:4000], has_alert, ", ".join(all_alert_names)

    except Exception as e:
        return f"\u274c \u041e\u0448\u0438\u0431\u043a\u0430: {str(e)[:200]}", False, ""
