import logging

from google.cloud import dialogflow
from google.oauth2 import service_account

bot_logger = logging.getLogger(__file__)


def detect_intent_texts(env, project_id, session_id, text, language_code):
    credentials = service_account.Credentials.from_service_account_file(
        env.str('GOOGLE_APPLICATION_CREDENTIALS')
    )
    session_client = dialogflow.SessionsClient(credentials=credentials)

    session = session_client.session_path(project_id, session_id)
    bot_logger.info("Session path: {}\n".format(session))

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
