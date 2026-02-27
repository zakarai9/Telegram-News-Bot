import os
import requests
from google import genai
from dotenv import load_dotenv

# Load environment variables (.env file for local run)
load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_news():
    # Fetch top 10 news articles in requested topics. (lang=ar for Arabic)
    query = '("إيران" OR "الشرق الأوسط" OR "الذكاء الاصطناعي" OR "استخدامات الذكاء" OR "المغرب" OR "تريندات")'
    url = f"https://gnews.io/api/v4/search?q={query}&lang=ar&max=10&apikey={GNEWS_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return data.get("articles", [])
        else:
            print(f"Error fetching news: {data}")
            return []
    except Exception as e:
        print(f"Error in requests: {e}")
        return []

def summarize_news(articles):
    if not articles:
        return "لا توجد أخبار جديدة حالياً. 🤷‍♂️"
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    summaries = []
    
    import time
    
    for index, article in enumerate(articles, 1):
        title = article.get("title", "")
        description = article.get("description", "")
        content = article.get("content", "")
        url = article.get("url", "")
        
        prompt = f"""
        قم بتلخيص هذا الخبر باختصار واحترافية بالدارجة المغربية المفهومة بشكل مشوق للقراءة في تيليجرام.
        لا تضف أي مقدمات أو خاتمات، فقط قدم الملخص في 3 أو 4 أسطر على الأكثر مع إيموجي مناسب.
        
        العنوان: {title}
        الوصف: {description}
        النص: {content}
        """
        
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            summary_text = response.text.strip()
            msg = f"📰 *{title}*\n\n{summary_text}\n\n🔗 [قرا المزيد هنا]({url})"
            summaries.append(msg)
            time.sleep(4) # To avoid Google GenAI free tier rate limits (15 RPM)
        except Exception as e:
            print(f"Error summarizing article {index}: {e}")
            summaries.append(f"📰 *{title}*\n\n(تعذر التلخيص بالذكاء الاصطناعي)\n\n🔗 [قرا المزيد هنا]({url})")
            time.sleep(4)
            
    # Combine summaries separate by lines
    final_message = "🔥 *أهم 10 أخبار فهاد الساعتين* 🔥\n\n➖➖➖➖➖➖➖➖\n\n"
    final_message += "\n\n➖➖➖➖➖➖➖➖\n\n".join(summaries)
    
    return final_message

def send_telegram_message(text):
    if not text:
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True # To make the message cleaner
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Message sent successfully to Telegram! ✅")
        else:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

if __name__ == "__main__":
    if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GNEWS_API_KEY, GEMINI_API_KEY]):
        print("خطأ: تأكد من إدخال جميع مفاتيح API و Chat ID الخاص بك.")
        exit(1)
        
    print("جاري البحث عن الأخبار...")
    latest_news = get_news()
    
    if latest_news:
        print("جاري صياغة التلخيص بالذكاء الاصطناعي...")
        summary = summarize_news(latest_news)
        
        print("جاري إرسال الرسالة إلى تيليجرام...")
        send_telegram_message(summary)
    else:
        print("لم أجد أي أخبار جديدة للأسف.")
