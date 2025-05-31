import os
import json
import random
import threading
from flask import Flask
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Переменные окружения
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

# Продукты по категориям
PRODUCTS = {
    "vbucks": [
        "💎 1000 В-баксов — 649₽",
        "💎 2800 В-баксов — 1699₽",
        "💎 5000 В-баксов — 2699₽",
        "💎 13500 В-баксов — 5399₽"
    ],
    "packs": [
        "🎒 Набор «Сагуаро» — 399₽",
        "🎒 Набор «Революция Граффити» — 399₽",
        "🎒 Набор «Час Расплаты» — 1299₽",
        "🎒 Набор «Ниндзя Сара» — 1299₽",
        "🎒 Набор «Легенды Анимэ» — 1499₽"
    ],
    "teams": [
        "🛡 Отряд «Epic Турция» — 499₽",
        "🛡 Отряд «Xbox» — 1499₽"
    ]
}

# Отправка сообщения
def send_message(user_id, message, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        keyboard=json.dumps(keyboard) if keyboard else None,
        random_id=random.randint(1, 2**31 - 1)
    )

# Главное меню
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
                        "label": "💰 Узнать цены",
                        "payload": json.dumps({"button": "show_prices"})
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "📄 Условия использования",
                        "payload": json.dumps({"button": "terms"})
                    },
                    "color": "primary"
                },
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

# Подменю цен
def get_price_menu():
    return {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "🔹 В-баксы",
                        "payload": json.dumps({"button": "vbucks"})
                    },
                    "color": "primary"
                },
                {
                    "action": {
                        "type": "text",
                        "label": "🔸 Наборы",
                        "payload": json.dumps({"button": "packs"})
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "🔻 Отряды",
                        "payload": json.dumps({"button": "teams"})
                    },
                    "color": "primary"
                },
                {
                    "action": {
                        "type": "text",
                        "label": "↩ Назад",
                        "payload": json.dumps({"button": "back_to_main"})
                    },
                    "color": "secondary"
                }
            ]
        ]
    }

# Основной цикл бота
def bot_loop():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
            message = event.object.message
            user_id = message['from_id']

            payload = message.get('payload')

            if not payload:
                text = message['text'].lower()
                if text in ['начать', 'start', 'привет', 'ку', 'здарова', 'здаров', 'хай']:
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

            elif button == 'show_prices':
                send_message(user_id, "💰 Выберите категорию:", keyboard=get_price_menu())

            elif button in ['vbucks', 'packs', 'teams']:
                items = PRODUCTS.get(button, [])
                text = "\n".join(items) if items else "🔍 В этой категории пока нет товаров."
                send_message(user_id, text, keyboard=get_price_menu())

            elif button == 'back_to_main':
                send_message(user_id, "🔙 Возврат в главное меню:", keyboard=get_keyboard())

            else:
                send_message(user_id, "❓ Я не понимаю. Пожалуйста, выберите действие из меню.", keyboard=get_keyboard())

# Запуск бота в отдельном потоке
threading.Thread(target=bot_loop, daemon=True).start()

# Flask-сервер
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
