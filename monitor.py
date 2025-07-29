import os
import feedparser
import requests
import json

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

STATE_FILE = 'last_seen.json'

def load_last_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_last_seen(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'disable_web_page_preview': True}
    requests.post(url, data=payload)

def fetch_latest_entry_title(url):
    feed = feedparser.parse(url)
    if feed.entries:
        entry = feed.entries[0]
        return entry.title, entry.link
    return None, None

def main():
    state = load_last_seen()

    with open('url_list.txt') as f:
        urls = f.read().splitlines()

    updated_state = {}

    for url in urls:
        title, link = fetch_latest_entry_title(url)
        if title and (url not in state or state[url] != title):
            send_telegram_message(f"🆕 New post from {url}:\n{title}\n{link}")
        updated_state[url] = title

    save_last_seen(updated_state)

if __name__ == '__main__':
    main()
