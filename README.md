
# Распознаём речь
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
git clone https://github.com/wombatoff/dvmn_5
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
GOOGLE_APPLICATION_CREDENTIALS=
GOOGLE_PROJECT_ID=
VK_TOKEN=
```

Запустить бота:
```
python telegram_bot.py
python vk_bot.py
```


## Запуск проекта на сервере
### Подготовка сервера
- Запустить сервер и подключиться к нему:
```
ssh username@ip_address
```
- Установить обновления apt:
```
sudo apt upgrade -y
```
- Установить docker:
```
sudo apt-get install docker.io -y
```

- Клонировать репозиторий и перейти в него:
```
git clone https://github.com/wombatoff/dvmn_5
cd dvmn_5
```
- Создать файл .env и заполнить его:
```
TELEGRAM_CHAT_ID=
GOOGLE_APPLICATION_CREDENTIALS=
GOOGLE_PROJECT_ID=
VK_TOKEN=
```
- Разверните Docker-контейнер:
```
sudo docker build -t dvmn_smart_bot .
```
```
sudo docker run -d \
  --name dvmn_smart_bot \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env \
  --env-file .env \
  --restart unless-stopped \
  dvmn_smart_bot \
  python dvmn_smart_bot.py
```

### Автор:

[Wombatoff](https://github.com/wombatoff/)