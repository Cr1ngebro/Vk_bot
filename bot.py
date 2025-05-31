import os
import json
import random
import threading
from flask import Flask
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Загружаем переменные окружения
GROUP_TOKEN = os.getenv("GROUP_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
GROUP_ID = int(os.getenv("GROUP_ID"))
PAYMENT_DETAILS = os.getenv("PAYMENT_DETAILS")

# Инициализация VK API
vk_session = vk_api.VkApi(token=GROUP_TOKEN)
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)
vk = vk_session.get_api()

# Flask-приложение
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Bot is running."

def send_message(user_id, message, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        keyboard=json.dumps(keyboard) if keyboard else None,
        random_id=random.randint(1, 2**31 - 1)
    )

def get_keyboard():
    return {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "📥 Реквизиты",
                        "payload": json.dumps({"button": "payment_details"})
                    },
                    "color": "positive"
                },
                {
                    "action": {
                        "type": "text",
                        "label": "📄 Условия использования",
                        "payload": json.dumps({"button": "terms"})
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "🆘 Позвать админа",
                        "payload": json.dumps({"button": "call_admin"})
                    },
                    "color": "negative"
                }
            ]
        ]
    }

def bot_loop():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
            message = event.object.message
            user_id = message['from_id']

            payload = message.get('payload')

            if not payload:
                text = message['text'].lower()
                if text in ['начать', 'start', 'привет']:
                    send_message(user_id, "👋 Добро пожаловать! Выберите действие:", keyboard=get_keyboard())
                continue

            try:
                data = json.loads(payload)
                button = data.get('button')
            except:
                button = None

            if button == 'payment_details':
                send_message(user_id, PAYMENT_DETAILS or "⚠ Реквизиты временно недоступны. Попробуйте позже.")
            elif button == 'terms':
                send_message(user_id, "📌 Условия использования:\n1. https://vk.com/wall-219520002_32382")
            elif button == 'call_admin':
                send_message(user_id, "✅ Админ скоро свяжется с вами.")
                send_message(ADMIN_ID, f"🔔 Вас вызывает пользователь: https://vk.com/id{user_id}")
            else:
                send_message(user_id, "❓ Я не понимаю. Пожалуйста, выберите действие из меню.", keyboard=get_keyboard())

# Запускаем longpoll в отдельном потоке
threading.Thread(target=bot_loop, daemon=True).start()

# Запускаем Flask сервер
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
