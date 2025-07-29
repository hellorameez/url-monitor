import feedparser
import hashlib
import os
import requests

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def fetch_latest_entry_title(url):
    feed = feedparser.parse(url)
    if feed.entries:
        return feed.entries[0].title + feed.entries[0].link
    return None

def get_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'disable_web_page_preview': False
    }
    requests.post(url, data=payload)

with open('url_list.txt') as f:
    urls = f.read().splitlines()

if not os.path.exists('seen_hashes.txt'):
    open('seen_hashes.txt', 'w').close()

with open('seen_hashes.txt') as f:
    seen_hashes = set(f.read().splitlines())

new_hashes = set()

for url in urls:
    latest = fetch_latest_entry_title(url)
    if not latest:
        continue
    content_hash = get_hash(latest)
    if content_hash not in seen_hashes:
        send_telegram_message(f"📰 New Post:\n{latest}")
        new_hashes.add(content_hash)

with open('seen_hashes.txt', 'a') as f:
    for h in new_hashes:
        f.write(h + '\n')
