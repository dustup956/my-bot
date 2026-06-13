import os

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = int(os.environ.get("TELEGRAM_CHANNEL_ID", "0"))

API_URL = "https://grow-a-garden-2-tracker.onrender.com/api/stock"
API_TIMEOUT = 15

RESTOCK_INTERVAL = 300
RESTOCK_BUFFER = 2

EMOJI_MAP = {
    "carrot": "\U0001f955", "tomato": "\U0001f345", "strawberry": "\U0001f353",
    "blueberry": "\U0001fad0", "corn": "\U0001f33d", "bamboo": "\U0001f38b",
    "pumpkin": "\U0001f383", "apple": "\U0001f34e", "banana": "\U0001f34c",
    "mango": "\U0001f96d", "dragon": "\U0001f409", "pineapple": "\U0001f34d",
    "grape": "\U0001f347", "mushroom": "\U0001f344", "cactus": "\U0001f335",
    "cherry": "\U0001f352", "sunflower": "\U0001f33b", "tulip": "\U0001f337",
    "coconut": "\U0001f965", "acorn": "\U0001f330", "pomegranate": "\U0001f351",
    "venus": "\U0001f33f", "poison": "\u2620\ufe0f", "moon": "\U0001f338",
    "green bean": "\U0001fad8", "bean": "\U0001fad8",
    "dragon's breath": "\U0001f525",
    "watering": "\U0001f6bf", "sprinkler": "\U0001f4a6",
    "trowel": "\u26cf\ufe0f", "lantern": "\U0001f3ee",
    "wheelbarrow": "\U0001f6fb", "gnome": "\U0001f5ff",
    "teleporter": "\U0001f535", "sign": "\U0001faea",
    "ladder": "\U0001fa9c", "bench": "\U0001fa91",
    "light": "\U0001f4a1", "arch": "\U0001f3db\ufe0f",
    "bridge": "\U0001f309", "fence": "\U0001f6a7",
    "bear trap": "\U0001faa4",
    "invisibility": "\U0001f47b", "speed": "\u26a1",
    "jump": "\U0001f998", "shrink": "\U0001f53d",
    "supersize": "\U0001f53c", "flashbang": "\U0001f4a5",
    "pot": "\U0001fab4",
}

RARITY_EMOJI = {
    "common":    "\U0001f7e2",
    "uncommon":  "\U0001f535",
    "rare":      "\u2b50",
    "epic":      "\U0001f525",
    "legendary": "\U0001f31f",
    "mythic":    "\U0001f48e",
    "super":     "\U0001f52e",
}

DEFAULT_ITEM_EMOJI = "\U0001f331"
DEFAULT_RARITY_EMOJI = "\U0001f7e2"

ALERT_RARITIES = frozenset(["legendary", "mythic", "super"])

SHOP_SECTIONS = [
    ("SeedShop_Normal", "\U0001f331 **SEEDS**"),
    ("GearShop",        "\u2699\ufe0f **GEAR**"),
    ("CrateShop",       "\U0001f4e6 **CRATES**"),
]
