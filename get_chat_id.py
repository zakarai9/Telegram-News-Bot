import requests
import sys

TOKEN = "8799567187:AAHFFt3fU26pOkdhkkclIKDTuMGc5KamGys"

def get_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url)
    data = response.json()
    
    if data.get("ok") and data.get("result"):
        # Get the latest message Chat ID
        chat_id = data["result"][-1]["message"]["chat"]["id"]
        username = data["result"][-1]["message"]["from"].get("first_name", "User")
        print(f"\n✅ تم العثور على رسالة من {username}!")
        print(f"🔹 الـ Chat ID ديالك هو: {chat_id}\n")
        return chat_id
    else:
        print("\n❌ لم أجد أي رسالة جديدة.")
        print("سير لتيليجرام قلب على @zakarai2_bot وكليكي على Start، عاد جرب هاد الكود مرة أخرى.\n")
        return None

if __name__ == "__main__":
    get_updates()
