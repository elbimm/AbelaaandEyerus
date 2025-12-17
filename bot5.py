# import os
# from telegram import Update
# from telegram.ext import (
#     Application, CommandHandler, MessageHandler, ConversationHandler,
#     ContextTypes, filters
# )
# from dotenv import load_dotenv

# # Load .env
# load_dotenv()
# TOKEN = os.getenv("TOKEN")
# ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# # Conversation states
# ASK_NAME, WAIT_PHOTO, WAIT_VIDEO = range(3)

# # ---------- Helper ----------
# def get_user_name(update, context):
#     if context.user_data.get("full_name"):
#         return context.user_data["full_name"]

#     u = update.effective_user
#     if not u:
#         return "Unknown"

#     name = getattr(u, "full_name", None)
#     if name:
#         return name

#     last = (u.last_name or "").strip()
#     return f"{u.first_name} {last}".strip() or "Unknown"


# # ---------- Commands ----------
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         "👋 Welcome to the Wedding Memories Bot!\n\n"
#         "You can share your memory:\n"
#         "📸 /sendimage – Send a wedding image\n"
#         "🎥 /sendvideo – Send a wedding video\n"
#         "✍️ /setname – Set your name manually"
#     )


# async def setname(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("👤 Enter your full name:")
#     return ASK_NAME


# async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     name = update.message.text.strip()
#     if len(name) < 2:
#         await update.message.reply_text("⚠️ Enter a valid full name:")
#         return ASK_NAME

#     context.user_data["full_name"] = name
#     await update.message.reply_text("✅ Name saved!\nNow choose /sendimage or /sendvideo")
#     return ConversationHandler.END


# # ---------- IMAGE FLOW ----------
# async def sendimage(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not context.user_data.get("full_name"):
#         await update.message.reply_text("👤 Enter your full name first:")
#         return ASK_NAME

#     await update.message.reply_text("📸 Please send the wedding image:")
#     return WAIT_PHOTO


# async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         if not update.message.photo:
#             await update.message.reply_text("⚠️ Please send a real photo.")
#             return WAIT_PHOTO

#         sender = get_user_name(update, context)
#         photo_id = update.message.photo[-1].file_id

#         # Send to admin instantly
#         await context.bot.send_message(ADMIN_ID, f"📸 New memory from {sender}")
#         await context.bot.send_chat_action(ADMIN_ID, "upload_photo")
#         await context.bot.send_photo(ADMIN_ID, photo_id)

#         await update.message.reply_text("❤️ Thanks for sharing your memory!")
#         return ConversationHandler.END

#     except Exception as e:
#         print("Image Error:", e)
#         await update.message.reply_text("⚠️ Upload timed out, try again.")
#         return WAIT_PHOTO


# # ---------- VIDEO FLOW ----------
# async def sendvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not context.user_data.get("full_name"):
#         await update.message.reply_text("👤 Enter your full name first:")
#         return ASK_NAME

#     await update.message.reply_text("🎥 Please send the wedding video:")
#     return WAIT_VIDEO


# async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         if not update.message.video:
#             await update.message.reply_text("⚠️ Please send a real video.")
#             return WAIT_VIDEO

#         sender = get_user_name(update, context)
#         video_id = update.message.video.file_id

#         # Send to admin instantly
#         await context.bot.send_message(ADMIN_ID, f"🎥 New memory from {sender}")
#         await context.bot.send_chat_action(ADMIN_ID, "upload_video")
#         await context.bot.send_video(ADMIN_ID, video_id)

#         await update.message.reply_text("❤️ Thanks for sharing your memory!")
#         return ConversationHandler.END

#     except Exception as e:
#         print("Video Error:", e)
#         await update.message.reply_text("⚠️ Upload timed out, try again.")
#         return WAIT_VIDEO


# # ---------- Cancel ----------
# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("❌ Cancelled.")
#     return ConversationHandler.END


# # ---------- Main ----------
# def main():
#     app = (
#         Application.builder()
#         .token(TOKEN)
#         .read_timeout(60)
#         .write_timeout(60)
#         .connect_timeout(60)
#         .build()
#     )

#     name_conv = ConversationHandler(
#         entry_points=[CommandHandler("setname", setname)],
#         states={ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)]},
#         fallbacks=[CommandHandler("cancel", cancel)],
#     )

#     image_conv = ConversationHandler(
#         entry_points=[CommandHandler("sendimage", sendimage)],
#         states={WAIT_PHOTO: [MessageHandler(filters.PHOTO, handle_image)],
#                 ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)]},
#         fallbacks=[CommandHandler("cancel", cancel)],
#     )

#     video_conv = ConversationHandler(
#         entry_points=[CommandHandler("sendvideo", sendvideo)],
#         states={WAIT_VIDEO: [MessageHandler(filters.VIDEO, handle_video)],
#                 ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)]},
#         fallbacks=[CommandHandler("cancel", cancel)],
#     )

#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(name_conv)
#     app.add_handler(image_conv)
#     app.add_handler(video_conv)

#     print("🤖 Wedding Bot running...")
#     app.run_polling()


# if __name__ == "__main__":
#     main()
