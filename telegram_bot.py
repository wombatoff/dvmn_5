import logging
import os
from logging.handlers import TimedRotatingFileHandler

from environs import Env
from telegram.ext import Updater, MessageHandler, Filters

from dialogflow_interaction import detect_intent_texts

bot_logger = logging.getLogger(__file__)


def handle_message_tl(env, update, context):
    try:
        session_id = update.effective_chat.id
        text = update.message.text
        language_code = 'ru'

        project_id = env.str('GOOGLE_PROJECT_ID')
        response_text = detect_intent_texts(env, project_id, session_id, text, language_code)

        if response_text and not response_text.intent.is_fallback:
            context.bot.send_message(chat_id=update.effective_chat.id, text=response_text.fulfillment_text)
    except Exception as e:
        bot_logger.exception("An error occurred while handling the message")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка при обработке сообщения.")


def main():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    log_file = os.path.join("logs", "telegram_bot.log")
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    bot_logger.setLevel(logging.DEBUG)
    bot_logger.addHandler(file_handler)

    env = Env()
    env.read_env()

    telegram_token = env.str("TELEGRAM_TOKEN")

    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        MessageHandler(Filters.text, lambda update, context: handle_message_tl(env, update, context)))
    updater.start_polling()


if __name__ == "__main__":
    main()
