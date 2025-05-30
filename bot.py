
import os
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
        keyboard=keyboard,
        random_id=0
    )

def get_keyboard():
    return {
        "one_time": False,
        "buttons": [
            [
                {"action": {"type": "text", "label": "📥 Получить реквизиты"}, "color": "positive"},
                {"action": {"type": "text", "label": "📄 Условия использования"}, "color": "primary"}
            ],
            [
                {"action": {"type": "text", "label": "🆘 Позвать админа"}, "color": "negative"}
            ]
        ]
    }

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
        text = event.object.message['text'].lower()
        user_id = event.object.message['from_id']

        if text in ['начать', 'start', 'привет']:
            send_message(user_id, "👋 Добро пожаловать! Выберите действие:", keyboard=get_keyboard())
        elif text == '📥 получить реквизиты':
            send_message(user_id, "💳 Реквизиты для оплаты:
Карта: 1234 5678 9012 3456
Имя: Иван Иванов")
        elif text == '📄 условия использования':
            send_message(user_id, "📌 Условия использования:
1. Оплата не возвращается.
2. Услуги предоставляются в течение 24 часов.")
        elif text == '🆘 позвать админа':
            send_message(user_id, "✅ Админ скоро свяжется с вами.")
            send_message(ADMIN_ID, f"🔔 Вас вызывает пользователь: https://vk.com/id{user_id}")
        else:
            send_message(user_id, "❓ Я не понимаю. Пожалуйста, выберите действие из меню.", keyboard=get_keyboard())
