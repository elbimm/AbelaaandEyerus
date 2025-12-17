import os
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes,
    filters
)
from dotenv import load_dotenv

# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------
load_dotenv()
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN or ADMIN_ID == 0:
    raise ValueError("❌ TOKEN or ADMIN_ID missing in .env file!")

# ---------------------------------------------------
# Helper: get user display name
# ---------------------------------------------------
def get_user_name(update, context):
    u = update.effective_user
    if not u:
        return "Unknown"
    return f"{u.full_name}" if u.full_name else f"{u.first_name} {(u.last_name or '').strip()}".strip() or "Unknown"

# ---------------------------------------------------
# Helper: caption for admin forwarded messages (User ID removed)
# ---------------------------------------------------
def admin_caption(update, context, media_type: str) -> str:
    user = update.effective_user
    name = get_user_name(update, context)
    return (
        f"**{media_type} MEMORY SUBMISSION**\n"
        f"**From:** {name} (@{user.username})\n\n"
        "--- Original Message ---\n"
    )

# ---------------------------------------------------
# /start
# ---------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "You can now send your wedding memories directly:\n"
        "📸 Send a photo\n"
        "🎥 Send a video\n\n"
        "Use /cancel anytime to stop."
    )

# ---------------------------------------------------
# HANDLE IMAGE
# ---------------------------------------------------
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.message
        if not (msg.photo or (msg.document and "image" in msg.document.mime_type)):
            await msg.reply_text("⚠️ Please send a valid image file.")
            return

        caption = admin_caption(update, context, "📸 PHOTO") + (msg.caption or "")

        await context.bot.copy_message(
            chat_id=ADMIN_ID,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )

        await msg.reply_text("❤️ Thanks for sharing your photo!")

    except Exception as e:
        logger.error(f"Image error: {e}")
        await msg.reply_text("⚠️ Error uploading. File may be too large.")

# ---------------------------------------------------
# HANDLE VIDEO
# ---------------------------------------------------
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.message
        if not (msg.video or (msg.document and "video" in msg.document.mime_type)):
            await msg.reply_text("⚠️ Please send a valid video file.")
            return

        caption = admin_caption(update, context, "🎥 VIDEO") + (msg.caption or "")

        await context.bot.copy_message(
            chat_id=ADMIN_ID,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )

        await msg.reply_text("❤️ Thanks for sharing your video!")

    except Exception as e:
        logger.error(f"Video error: {e}")
        await msg.reply_text("⚠️ Error uploading. File may be too large.")

# ---------------------------------------------------
# CANCEL
# ---------------------------------------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Submission cancelled.")

# ---------------------------------------------------
# ERROR HANDLER
# ---------------------------------------------------
async def error_handler(update, context):
    logger.error(f"Exception: {context.error}")
    if update and update.effective_chat:
        await update.effective_chat.send_message("⚠️ Unexpected error occurred. Try again.")

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    app.add_error_handler(error_handler)

    logger.info("🤖 Wedding Memories Bot running…")
    app.run_polling()

if __name__ == "__main__":
    main()
