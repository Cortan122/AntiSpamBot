import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN, COMMAND_AUTO_DELETE_SECONDS, SPAM_FLAG_EMOJI
from db import (
    init_db, add_spam_pattern, get_spam_patterns, get_user_message_count,
    increment_user_message_count, log_admin_action, is_user_blocked, block_user,
    clear_spam_pattern
)
from similarity import find_similar_spam

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def delete_message_later(bot, chat_id, message_id):
    """Delete a message after COMMAND_AUTO_DELETE_SECONDS."""
    await asyncio.sleep(COMMAND_AUTO_DELETE_SECONDS)
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        logger.warning(f"Could not delete message: {e}")


async def is_admin(context: ContextTypes.DEFAULT_TYPE, group_id: int, user_id: int) -> bool:
    """Check if a user is an admin in a group."""
    try:
        member = await context.bot.get_chat_member(group_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text("Hi! I am an anti-spam bot. Use /addspam to add spam patterns (admin only).")


async def addspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addspam command - admins add spam patterns."""
    if not update.message.chat.type in ['group', 'supergroup']:
        return

    group_id = update.message.chat_id
    user_id = update.message.from_user.id

    # Check admin permissions
    if not await is_admin(context, group_id, user_id):
        return

    spam_text = None

    # If used as a reply, get the replied message
    if update.message.reply_to_message:
        spam_text = update.message.reply_to_message.text
    # Otherwise, get the text after /addspam
    elif context.args:
        spam_text = ' '.join(context.args)

    if not spam_text:
        return

    try:
        add_spam_pattern(group_id, spam_text)
        log_admin_action(group_id, 'add_spam', spam_text)
        logger.info(f"Added spam pattern to group {group_id}: {spam_text[:50]}")
    except Exception as e:
        logger.error(f"Error adding spam pattern: {e}")

    # Delete the command message after COMMAND_AUTO_DELETE_SECONDS
    asyncio.create_task(delete_message_later(context.bot, group_id, update.message.message_id))


async def spamlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /spamlist command - show spam patterns (admin only)."""
    if not update.message.chat.type in ['group', 'supergroup']:
        return

    group_id = update.message.chat_id
    user_id = update.message.from_user.id

    # Check admin permissions
    if not await is_admin(context, group_id, user_id):
        return

    patterns = get_spam_patterns(group_id)

    if not patterns:
        message_text = "No spam patterns in this group yet."
    else:
        lines = ["Spam patterns in this group:"]
        for pattern_id, text, _ in patterns:
            lines.append(f"{pattern_id}. {text[:50]}{'...' if len(text) > 50 else ''}")
        message_text = "\n".join(lines)

    try:
        sent_msg = await update.message.reply_text(message_text)
        asyncio.create_task(delete_message_later(context.bot, group_id, sent_msg.message_id))
        asyncio.create_task(delete_message_later(context.bot, group_id, update.message.message_id))
    except Exception as e:
        logger.error(f"Error handling spamlist: {e}")


async def clearspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clearspam command - remove a spam pattern (admin only)."""
    if not update.message.chat.type in ['group', 'supergroup']:
        return

    group_id = update.message.chat_id
    user_id = update.message.from_user.id

    # Check admin permissions
    if not await is_admin(context, group_id, user_id):
        return

    if not context.args:
        return

    try:
        pattern_id = int(context.args[0])
        clear_spam_pattern(pattern_id)
        log_admin_action(group_id, 'clear_spam', f"Pattern ID: {pattern_id}")
        logger.info(f"Cleared spam pattern {pattern_id} from group {group_id}")
    except (ValueError, Exception) as e:
        logger.error(f"Error clearing spam pattern: {e}")

    # Delete the command message after COMMAND_AUTO_DELETE_SECONDS
    asyncio.create_task(delete_message_later(context.bot, group_id, update.message.message_id))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages - check for spam."""
    if not update.message.chat.type in ['group', 'supergroup']:
        return

    group_id = update.message.chat_id
    user_id = update.message.from_user.id
    message_text = update.message.text

    if not message_text:
        return

    try:
        # Check if user is blocked
        if is_user_blocked(group_id, user_id):
            try:
                await context.bot.delete_message(group_id, update.message.message_id)
            except Exception as e:
                logger.warning(f"Could not delete blocked user message: {e}")
            return

        # Get user message count
        message_count = get_user_message_count(group_id, user_id)

        # Check for spam
        spam_patterns = get_spam_patterns(group_id)
        if spam_patterns:
            match = find_similar_spam(message_text, spam_patterns)

            if match:
                pattern_id, pattern_text, similarity = match

                if message_count == 0:
                    # First message - delete, block user, report
                    try:
                        await context.bot.delete_message(group_id, update.message.message_id)
                    except Exception as e:
                        logger.warning(f"Could not delete user's first spam message: {e}")

                    # Block user
                    block_user(group_id, user_id)

                    # Report to admins
                    report_text = (
                        f"🚨 First spam message detected and blocked!\n"
                        f"User: {update.message.from_user.mention_html()}\n"
                        f"User ID: {user_id}\n"
                        f"Similarity: {similarity:.2%}"
                    )
                    try:
                        await context.bot.send_message(
                            chat_id=group_id,
                            text=report_text,
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        logger.error(f"Could not send admin report: {e}")

                    log_admin_action(group_id, 'block_user', f"User {user_id}, Similarity: {similarity:.2%}")
                    return
                else:
                    # Repeat spam - flag with emoji
                    try:
                        await context.bot.set_message_reaction(
                            chat_id=group_id,
                            message_id=update.message.message_id,
                            reaction=SPAM_FLAG_EMOJI
                        )
                    except Exception as e:
                        logger.warning(f"Could not set reaction: {e}")

                    log_admin_action(group_id, 'flag_spam', f"User {user_id}, Similarity: {similarity:.2%}")

        # Increment message count
        increment_user_message_count(group_id, user_id)

    except Exception as e:
        logger.error(f"Error processing message: {e}")


def main():
    """Main function to start the bot."""
    if not TELEGRAM_TOKEN:
        print("Error: No TELEGRAM_TOKEN found in environment variables.")
        return

    # Initialize database
    init_db()

    # Build the application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addspam", addspam))
    application.add_handler(CommandHandler("spamlist", spamlist))
    application.add_handler(CommandHandler("clearspam", clearspam))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("Bot is starting...")
    application.run_polling()


if __name__ == '__main__':
    main()
