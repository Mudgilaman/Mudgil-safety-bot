import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Logging setup (errors track karne ke liye)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Yeh variables environment se aayenge (Render pe secure rahega)
TOKEN = "8316442697:AAE7XDHgOMBbREzD5Q4Tnb8yYnYVIjIr8YE"  # Render pe env var se replace hoga, yahan placeholder rakh lo
YOUR_TELEGRAM_ID = @amanmudgil  # Apna Telegram user ID daalo (bot se /myid command se check kar sakte ho agar add karo)

# Example NCR center (Delhi/Gurugram midpoint)
NCR_CENTER = (28.6139, 77.2090)  # India Gate coords

# Multiple users ke locations store karne ke liye (simple dict, production mein DB use karo)
user_locations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    keyboard = [
        [KeyboardButton("Share Live Location", request_location=True)],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Welcome to NCR Safety Tracker!\nShare your live location for tracking.",
        reply_markup=reply_markup,
    )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Location message ya live location update handler"""
    # Edited message for live updates, normal for one-time
    message = update.edited_message if update.edited_message else update.message

    if not message.location:
        return

    user_id = message.from_user.id
    lat = message.location.latitude
    lon = message.location.longitude

    # Store location
    user_locations[user_id] = {"lat": lat, "lon": lon, "time": message.date.isoformat()}

    # Simple distance from NCR center (example)
    from geopy.distance import geodesic
    distance_km = geodesic((lat, lon), NCR_CENTER).km

    maps_link = f"https://maps.google.com/?q={lat},{lon}"

    info = (
        f"User {user_id} shared location:\n"
        f"Lat: {lat:.6f}, Lon: {lon:.6f}\n"
        f"Distance from Delhi Center: {distance_km:.1f} km\n"
        f"Map: {maps_link}"
    )

    # Tumhe (owner) message bhej do
    await context.bot.send_message(chat_id=YOUR_TELEGRAM_ID, text=info)

    # User ko confirmation
    await message.reply_text("Location shared successfully! Stay safe in NCR.")

def main() -> None:
    """Main function to run the bot"""
    application = Application.builder().token(TOKEN).build()

    # Handlers add karo
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Live location updates ke liye (edited messages catch)
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_location))

    # Polling se start (Render pe free tier ke liye best)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
