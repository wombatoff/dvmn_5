
# Отправляем уведомления о проверке работ
### Описание
Telegram и VK бот, который отвечает на вопросы

### Стек технологий:
- Python
- python-telegram-bot
- Google dialogflow
- vk_api
---


## Запуск проекта локально
Клонировать репозиторий и перейти в него:
```
git clone https://github.com/wombatoff/dvmn_2
cd dvmn_5
```

Создать и активировать виртуальное окружение, обновить pip и установить зависимости:
```
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Создать файл .env и заполнить его:
```
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
GOOGLE_APPLICATION_CREDENTIALS=
GOOGLE_PROJECT_ID=
VK_TOKEN=
```

Запустить бота:
```
python dvmn_checker.py
```

### Автор:

[Wombatoff](https://github.com/wombatoff/)