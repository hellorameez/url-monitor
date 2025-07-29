
import os
import requests
import feedparser
import openai

openai.api_key = os.environ['OPENAI_API_KEY']

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def detect_category_ai(title, summary):
    prompt = f"""Title: {title}
Summary: {summary}

Classify this article into one of the following categories:
- Apple
- Android
- Mobile
- Tech
- Other

Return only the category name."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in tech news classification."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        category = response.choices[0].message['content'].strip()
        return category
    except Exception as e:
        return "Other"

def format_message(title, link, summary):
    category = detect_category_ai(title, summary)
    return f"<b>📢 [{category}]</b>\n<b>{title}</b>\n<b>Summary:</b> {summary}\n🔗 {link}"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

def get_last_notified_titles():
    if os.path.exists("notified.txt"):
        with open("notified.txt", "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def update_notified_titles(titles):
    with open("notified.txt", "a", encoding="utf-8") as f:
        for title in titles:
            f.write(title + "\n")

def main():
    with open("url_list.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    already_notified = get_last_notified_titles()
    new_titles = []

    for url in urls:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            title = entry.title.strip()
            link = entry.link.strip()
            summary = entry.get("summary", "").strip()[:300]
            if title not in already_notified:
                message = format_message(title, link, summary)
                send_telegram_message(message)
                new_titles.append(title)

    update_notified_titles(new_titles)

if __name__ == "__main__":
    main()
