import requests
import time
import config

def get_chat_id():
    print("Ожидание сообщения боту для получения Chat ID... (Напишите боту /start или любое сообщение)")
    offset = 0
    start_time = time.time()
    
    # Try for 60 seconds
    while time.time() - start_time < 60:
        try:
            url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates?offset={offset}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    offset = update['update_id'] + 1
                    message = update.get('message') or update.get('channel_post') or update.get('my_chat_member')
                    
                    if message:
                        chat = message.get('chat')
                        if chat:
                            print(f"\nУСПЕХ! Найден Chat ID: {chat['id']}")
                            print(f"Тип чата: {chat['type']}")
                            print(f"Название/Имя: {chat.get('title') or chat.get('username') or chat.get('first_name')}")
                            return chat['id']
            time.sleep(2)
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            time.sleep(2)
            
    print("\nНе удалось получить сообщения. Убедитесь, что вы написали боту.")
    return None

if __name__ == "__main__":
    get_chat_id()
