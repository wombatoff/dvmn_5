import logging
import os
from logging.handlers import TimedRotatingFileHandler

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

import telegram
from environs import Env
from google.cloud import dialogflow
from google.oauth2 import service_account
from telegram.ext import Updater, MessageHandler, Filters

bot_logger = logging.getLogger(__file__)


def detect_intent_texts(env, project_id, session_id, texts, language_code):
    credentials = service_account.Credentials.from_service_account_file(
        env.str('GOOGLE_APPLICATION_CREDENTIALS')
    )
    session_client = dialogflow.SessionsClient(credentials=credentials)

    session = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session))

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        print("=" * 20)
        print("Query text: {}".format(response.query_result.query_text))
        print(
            "Detected intent: {} (confidence: {})\n".format(
                response.query_result.intent.display_name,
                response.query_result.intent_detection_confidence,
            )
        )
        print("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))

        return response.query_result.fulfillment_text


def main():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    log_file = os.path.join("logs", "log_file.log")
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
    telegram_chat_id = env.int("TELEGRAM_CHAT_ID")
    smart_bot = telegram.Bot(token=telegram_token)

    vk_token = env.str("VK_TOKEN")
    vk_session = vk_api.VkApi(token=vk_token)

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            print('Новое сообщение:')
            if event.to_me:
                print('Для меня от: ', event.user_id)
            else:
                print('От меня для: ', event.user_id)
            print('Текст:', event.text)

    def handle_message(update, context):
        try:
            project_id = env.str('GOOGLE_PROJECT_ID')
            session_id = update.effective_chat.id
            text = update.message.text
            language_code = 'ru'
            response_text = detect_intent_texts(env, project_id, session_id, [text], language_code)
            if response_text:
                context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Не совсем понял.")
        except Exception as e:
            bot_logger.exception("An error occurred while handling the message")
            context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка при обработке сообщения.")

    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    updater.start_polling()


if __name__ == "__main__":
    main()
