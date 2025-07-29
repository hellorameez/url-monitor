
import os
import requests
from bs4 import BeautifulSoup

URLS = [
    "https://www.beebom.com/",
    "https://gadgets360.com/news",
    "https://www.theverge.com/tech",
    "https://techcrunch.com/",
    "https://www.androidauthority.com/",
    "https://9to5google.com/",
    "https://www.macrumors.com/",
    "https://www.gsmarena.com/"
]

BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
STATE_FILE = "prev_links.txt"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': msg}
    requests.post(url, data=data)

def get_latest_link(site_url):
    try:
        res = requests.get(site_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        if "beebom" in site_url:
            article = soup.select_one("article a")
        elif "gadgets360" in site_url:
            article = soup.select_one(".story_list a")
        elif "theverge" in site_url:
            article = soup.select_one("h2 a")
        elif "techcrunch" in site_url:
            article = soup.select_one("a.post-block__title__link")
        elif "androidauthority" in site_url:
            article = soup.select_one("article h3 a")
        elif "9to5google" in site_url:
            article = soup.select_one("article header h2 a")
        elif "macrumors" in site_url:
            article = soup.select_one("div.article h2 a")
        elif "gsmarena" in site_url:
            article = soup.select_one("div.news-item a")
        else:
            return None

        if article and article.get("href"):
            link = article["href"]
            if not link.startswith("http"):
                link = site_url.rstrip("/") + "/" + link.lstrip("/")
            return link
    except Exception as e:
        print(f"Error fetching from {site_url}: {e}")
    return None

def load_previous():
    try:
        with open(STATE_FILE, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_current(links):
    with open(STATE_FILE, 'w') as f:
        for link in links:
            f.write(link + '\n')

def main():
    previous_links = load_previous()
    current_links = set()

    for url in URLS:
        latest_link = get_latest_link(url)
        if latest_link:
            current_links.add(latest_link)
            if latest_link not in previous_links:
                send_telegram(f"🆕 New post found: {latest_link}")

    save_current(current_links)

if __name__ == "__main__":
    main()
