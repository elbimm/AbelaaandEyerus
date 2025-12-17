# import os
# import logging
# from telegram import Update
# from telegram.constants import ParseMode
# from telegram.ext import (
#     Application, CommandHandler, MessageHandler, ConversationHandler,
#     ContextTypes, filters
# )
# from dotenv import load_dotenv

# # ---------------------------------------------------
# # LOGGING
# # ---------------------------------------------------
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# # ---------------------------------------------------
# # ENVIRONMENT
# # ---------------------------------------------------
# load_dotenv()
# TOKEN = os.getenv("TOKEN")
# ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# if not TOKEN or ADMIN_ID == 0:
#     raise ValueError("❌ TOKEN or ADMIN_ID missing in .env file!")

# # Conversation states
# ASK_NAME, WAIT_PHOTO, WAIT_VIDEO = range(3)

# # ---------------------------------------------------
# # Helper: get user display name
# # ---------------------------------------------------
# def get_user_name(update, context):
#     if context.user_data.get("full_name"):
#         return context.user_data["full_name"]

#     u = update.effective_user
#     if not u:
#         return "Unknown"

#     if u.full_name:
#         return u.full_name

#     last = (u.last_name or "").strip()
#     return f"{u.first_name} {last}".strip() or "Unknown"


# # ---------------------------------------------------
# # Helper: caption for admin forwarded messages (User ID removed)
# # ---------------------------------------------------
# def admin_caption(update, context, media_type: str) -> str:
#     user = update.effective_user
#     name = get_user_name(update, context)

#     return (
#         f"**{media_type} MEMORY SUBMISSION**\n"
#         f"**From:** {name} (@{user.username})\n\n"
#         "--- Original Message ---\n"
#     )


# # ---------------------------------------------------
# # /start
# # ---------------------------------------------------
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         "👋 Welcome!\n\n"
#         "To share your memories:\n"
#         "📝 /setname – Set your full name\n"
#         "📸 /sendimage – Send a wedding photo\n"
#         "🎥 /sendvideo – Send a wedding video"
#     )


# # ---------------------------------------------------
# # NAME HANDLING
# # ---------------------------------------------------
# async def setname(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("👤 Enter your full name:")
#     return ASK_NAME


# async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     name = update.message.text.strip()

#     if len(name) < 2:
#         await update.message.reply_text("⚠️ Please enter a valid full name:")
#         return ASK_NAME

#     context.user_data["full_name"] = name
#     await update.message.reply_text("✅ Name saved! Now choose /sendimage or /sendvideo.")
#     return ConversationHandler.END


# # ---------------------------------------------------
# # IMAGE FLOW
# # ---------------------------------------------------
# async def sendimage(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not context.user_data.get("full_name"):
#         await update.message.reply_text("Enter your full name first:")
#         return ASK_NAME

#     await update.message.reply_text("📸 Send your wedding photo now:")
#     return WAIT_PHOTO


# async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         msg = update.message

#         if not (msg.photo or (msg.document and "image" in msg.document.mime_type)):
#             await msg.reply_text("⚠️ Please send a valid image file.")
#             return WAIT_PHOTO

#         caption = admin_caption(update, context, "📸 PHOTO") + (msg.caption or "")

#         await context.bot.copy_message(
#             chat_id=ADMIN_ID,
#             from_chat_id=msg.chat_id,
#             message_id=msg.message_id,
#             caption=caption,
#             parse_mode=ParseMode.MARKDOWN
#         )

#         await msg.reply_text("❤️ Thanks for sharing your photo!")
#         return ConversationHandler.END

#     except Exception as e:
#         logger.error(f"Image error: {e}")
#         await msg.reply_text("⚠️ Error uploading. File may be too large.")
#         return WAIT_PHOTO


# # ---------------------------------------------------
# # VIDEO FLOW
# # ---------------------------------------------------
# async def sendvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not context.user_data.get("full_name"):
#         await update.message.reply_text("Enter your full name first:")
#         return ASK_NAME

#     await update.message.reply_text("🎥 Send your wedding video now:")
#     return WAIT_VIDEO


# async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         msg = update.message

#         if not (msg.video or (msg.document and "video" in msg.document.mime_type)):
#             await msg.reply_text("⚠️ Please send a valid video file.")
#             return WAIT_VIDEO

#         caption = admin_caption(update, context, "🎥 VIDEO") + (msg.caption or "")

#         await context.bot.copy_message(
#             chat_id=ADMIN_ID,
#             from_chat_id=msg.chat_id,
#             message_id=msg.message_id,
#             caption=caption,
#             parse_mode=ParseMode.MARKDOWN
#         )

#         await msg.reply_text("❤️ Thanks for sharing your video!")
#         return ConversationHandler.END

#     except Exception as e:
#         logger.error(f"Video error: {e}")
#         await msg.reply_text("⚠️ Error uploading. File may be too large.")
#         return WAIT_VIDEO


# # ---------------------------------------------------
# # CANCEL
# # ---------------------------------------------------
# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("❌ Submission cancelled.")
#     return ConversationHandler.END


# # ---------------------------------------------------
# # ERROR HANDLER
# # ---------------------------------------------------
# async def error_handler(update, context):
#     logger.error(f"Exception: {context.error}")
#     if update and update.effective_chat:
#         await update.effective_chat.send_message("⚠️ Unexpected error occurred. Try again.")


# # ---------------------------------------------------
# # MAIN
# # ---------------------------------------------------
# def main():
#     app = (
#         Application.builder()
#         .token(TOKEN)
#         .read_timeout(60)
#         .write_timeout(60)
#         .connect_timeout(60)
#         .build()
#     )

#     # Name
#     name_conv = ConversationHandler(
#         entry_points=[CommandHandler("setname", setname)],
#         states={ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)]},
#         fallbacks=[CommandHandler("cancel", cancel)],
#     )

#     # Image
#     image_conv = ConversationHandler(
#         entry_points=[CommandHandler("sendimage", sendimage)],
#         states={
#             WAIT_PHOTO: [MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image)],
#             ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)]
#         },
#         fallbacks=[CommandHandler("cancel", cancel)],
#     )

#     # Video
#     video_conv = ConversationHandler(
#         entry_points=[CommandHandler("sendvideo", sendvideo)],
#         states={
#             WAIT_VIDEO: [MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video)],
#             ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)]
#         },
#         fallbacks=[CommandHandler("cancel", cancel)],
#     )

#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(name_conv)
#     app.add_handler(image_conv)
#     app.add_handler(video_conv)
#     app.add_error_handler(error_handler)

#     logger.info("🤖 Wedding Memories Bot running…")
#     app.run_polling()


# if __name__ == "__main__":
#     main()
