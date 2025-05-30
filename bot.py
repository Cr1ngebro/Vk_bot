import os
import json
import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

GROUP_TOKEN = os.getenv("GROUP_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
GROUP_ID = int(os.getenv("GROUP_ID"))

vk_session = vk_api.VkApi(token=GROUP_TOKEN)
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)
vk = vk_session.get_api()

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
                        "label": "📥 Получить реквизиты",
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

# Для отправки приветствия по команде "начать" или "привет" оставим простую проверку на текст
# Но дальше бот реагирует ТОЛЬКО на payload от кнопок

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
        message = event.object.message
        user_id = message['from_id']

        # Если есть payload — значит, нажата кнопка
        payload = message.get('payload')
        
        # Обработка приветствия по тексту (без payload)
        if not payload:
            text = message['text'].lower()
            if text in ['начать', 'start', 'привет']:
                send_message(user_id, "👋 Добро пожаловать! Выберите действие:", keyboard=get_keyboard())
            # Игнорируем любые другие тексты
            continue
        
        # Если payload есть — парсим его
        try:
            data = json.loads(payload)
            button = data.get('button')
        except:
            button = None

        if button == 'payment_details':
            send_message(user_id, """💳 Реквизиты для оплаты:
Карта: 1234 5678 9012 3456
Имя: Иван Иванов""")

        elif button == 'terms':
            send_message(user_id, """📌 Условия использования:
1. Оплата не возвращается.
2. Услуги предоставляются в течение 24 часов.""")

        elif button == 'call_admin':
            send_message(user_id, "✅ Админ скоро свяжется с вами.")
            send_message(ADMIN_ID, f"🔔 Вас вызывает пользователь: https://vk.com/id{user_id}")

        else:
            send_message(user_id, "❓ Я не понимаю. Пожалуйста, выберите действие из меню.", keyboard=get_keyboard())
