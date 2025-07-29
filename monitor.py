import os
import feedparser
import requests
import json
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

STATE_FILE = 'last_seen.json'
FEED_FILE = 'url_list.txt'

def load_last_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_last_seen(data):
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f)

def send_telegram_message(title, link, source):
    timestamp = datetime.now().strftime("%d %b %Y • %I:%M %p")
    message = f"""
📢 *{source.upper()} Update*  
📰 *{title}*  
🔗 [View Full Post]({link})  
🕒 {timestamp}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    requests.post(url, data=payload)

def fetch_latest_entries(url, last_seen):
    feed = feedparser.parse(url)
    source = url.split('/')[2]

    if not feed.entries:
        return

    latest_title = feed.entries[0].title
    latest_link = feed.entries[0].link

    if last_seen.get(url) != latest_title:
        send_telegram_message(latest_title, latest_link, source)
        last_seen[url] = latest_title

def main():
    last_seen = load_last_seen()

    with open(FEED_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        fetch_latest_entries(url, last_seen)

    save_last_seen(last_seen)

if __name__ == "__main__":
    main()
