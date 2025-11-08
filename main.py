import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)
    
config = load_config()

DEBUG_MODE = config.get('DEBUG_MODE', False)
POST_DATA = config.get('post_data', {})
WEBHOOK_DATA = config.get('webhook_data', {})

WEBHOOK_URL = POST_DATA.get('discord_webhook', 'YOUR_DISCORD_WEBHOOK_URL_HERE')
WEBSITE_API_URL = POST_DATA.get('website_api_url', 'YOUR_API_URL_HERE')

if DEBUG_MODE:
    print(f"Loaded configuration: WEBHOOK_URL={WEBHOOK_URL}, WEBSITE_API_URL={WEBSITE_API_URL}")

if WEBHOOK_URL == 'YOUR_DISCORD_WEBHOOK_URL_HERE' and DEBUG_MODE:
    print("Discord Webhook URL is not set in config.json.")

if WEBSITE_API_URL == 'YOUR_API_URL_HERE' and DEBUG_MODE:
    print("Website API URL is not set in config.json.")

if WEBHOOK_URL == 'YOUR_DISCORD_WEBHOOK_URL_HERE' and WEBSITE_API_URL == 'YOUR_API_URL_HERE':
    print("ERROR: Please replace discord_webhook and/or website_api_url with your actual URL(s) in config.json.")
    exit(1)


url = 'https://store.steampowered.com/search?maxprice=free&supportedlang=french%2Cenglish&specials=1&ndl=1'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1'
}

seen_games = set()

def image_exists(image_url):
    if not image_url:
        return False
    try:
        response = requests.head(image_url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def send_discord_webhook(game):
    timestamp = datetime.utcnow().isoformat()
    
    header_image = game.get('header_image')
    search_thumbnail = game.get('search_thumbnail')
    thumbnail = 'https://store.steampowered.com/public/images/v6/icon_platform_win.png'
    
    if header_image and image_exists(header_image):
        thumbnail = header_image
    elif search_thumbnail and image_exists(search_thumbnail):
        thumbnail = search_thumbnail
    
    username = WEBHOOK_DATA.get('username', 'Game Tracker')
    mention_everyone = WEBHOOK_DATA.get('mention_everyone', False)
    mention_role_id = WEBHOOK_DATA.get('mention_role_id', None)
    
    content = ''
    if mention_everyone:
        content = '@everyone New free game on Steam!'
    elif mention_role_id:
        content = f'<@{mention_role_id}> New free game on Steam!'
    else:
        content = 'New free game on Steam!'
    
    payload = {
        'username': username,
        'content': content,
        'embeds': [
            {
                'title': game['title'],
                'url': game['url'],
                'description': f"Free on Steam! Price: {game['price']}",
                'color': 0x1B2838,
                'image': {'url': thumbnail},
                'timestamp': timestamp,
                'footer': {'text': 'Steam Free Games Monitor by SertraFurr'} #Please don't remove, but do all you want IG !
            }
        ]
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sent Discord notification for {game['title']}")
    except requests.RequestException as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Failed to send Discord notification: {e}")

def send_to_website(game):
    timestamp = datetime.utcnow().isoformat()
    game_data = game.copy()
    game_data['timestamp'] = timestamp
    
    api_headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(WEBSITE_API_URL, json=game_data, headers=api_headers)
        response.raise_for_status()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sent to website API for {game['title']}")
    except requests.RequestException as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Failed to send to website API: {e}")

def fetch_free_games():
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
       
        games = []
        for row in soup.find_all('a', class_='search_result_row'):
            app_id = row.get('data-ds-appid', 'N/A')
            title_elem = row.find('span', class_='title')
            title = title_elem.text.strip() if title_elem else 'N/A'
            discount_block = row.find('div', class_='discount_block search_discount_block')
            final_price = 'N/A'
            if discount_block:
                final_price_elem = discount_block.find('div', class_='discount_final_price')
                final_price = final_price_elem.text.strip() if final_price_elem else 'N/A'
            
            capsule = row.find('div', class_='search_capsule')
            search_thumbnail = None
            if capsule and capsule.find('img'):
                search_thumbnail = capsule.find('img')['src']
           
            header_image = None
            if app_id != 'N/A':
                header_image = f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{app_id}/header.jpg"
           
            href = row.get('href', '')
            full_url = f"https://store.steampowered.com{href}" if href and not href.startswith('http') else href or 'N/A'
            
            if final_price == '0,00€':
                games.append({
                    'app_id': app_id,
                    'title': title,
                    'url': full_url,
                    'price': final_price,
                    'header_image': header_image,
                    'search_thumbnail': search_thumbnail
                })
       
        return games
    except requests.RequestException as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error fetching data: {e}")
        return []

def check_for_new_games():
    global seen_games
    games = fetch_free_games()
    new_games = []
    
    for game in games:
        if game['app_id'] not in seen_games:
            new_games.append(game)
            seen_games.add(game['app_id'])
            
            if WEBHOOK_URL != 'YOUR_DISCORD_WEBHOOK_URL_HERE':
                send_discord_webhook(game)
            if WEBSITE_API_URL != 'YOUR_API_URL_HERE':
                send_to_website(game)
    
    if new_games:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Found {len(new_games)} new free games:")
        for game in new_games:
            print(f"- {game['title']}: {game['price']} | {game['url']}")
    return len(new_games) > 0

print("Starting Steam free games monitor with Discord embedded notifications as Game Tracker (checks every 60 seconds)...")

while True:
    check_for_new_games()
    time.sleep(60)
