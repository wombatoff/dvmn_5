import logging
import os
import random
from logging.handlers import TimedRotatingFileHandler

import telegram
import vk_api as vk
from environs import Env
from google.cloud import dialogflow
from google.oauth2 import service_account
from vk_api.longpoll import VkLongPoll, VkEventType

bot_logger = logging.getLogger(__file__)


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def detect_intent_texts(env, project_id, session_id, texts, language_code):
    credentials = service_account.Credentials.from_service_account_file(
        env.str('GOOGLE_APPLICATION_CREDENTIALS')
    )
    session_client = dialogflow.SessionsClient(credentials=credentials)

    session = session_client.session_path(project_id, session_id)
    bot_logger.info("Session path: {}\n".format(session))

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        bot_logger.info("Query text: {}".format(response.query_result.query_text))
        bot_logger.info(
            "Detected intent: {} (confidence: {})\n".format(
                response.query_result.intent.display_name,
                response.query_result.intent_detection_confidence,
            )
        )
        bot_logger.info("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))

        return response.query_result


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
    info_bot = telegram.Bot(token=telegram_token)
    telegram_handler = TelegramLogsHandler(info_bot, telegram_chat_id)
    telegram_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    telegram_handler.setLevel(logging.ERROR)
    bot_logger.addHandler(telegram_handler)

    bot_logger.setLevel(logging.DEBUG)

    vk_token = env.str("VK_TOKEN")
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    def handle_message(event, vk_api):
        try:
            project_id = env.str('GOOGLE_PROJECT_ID')
            session_id = event.user_id
            text = event.text
            language_code = 'ru'
            query_result = detect_intent_texts(env, project_id, session_id, [text], language_code)

            if query_result.fulfillment_text:
                vk_api.messages.send(
                    user_id=event.user_id,
                    message=query_result.fulfillment_text,
                    random_id=random.randint(1, 1000000)
                )

        except Exception as e:
            bot_logger.exception("An error occurred while handling the message")
            vk_api.messages.send(
                user_id=event.user_id,
                message="Произошла ошибка при обработке сообщения.",
                random_id=random.randint(1, 1000000)
            )

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event, vk_api)


if __name__ == "__main__":
    main()
