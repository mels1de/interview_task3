import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import pandas as pd
import time


def parse_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')

        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else 'No title'

        body = soup.find('article') or soup.find('div', class_=re.compile('article|content|body'))

        if not body:
            return {
                'title': title,
                'url': url,
                'word_count': 0,
                'paragraph_count': 0,
                'image_count': 0,
                'common_word': 'N/A',
                'tags': 'Not found'
            }

        paragraphs = [p for p in body.find_all('p') if p.get_text(strip=True)]
        text = ' '.join(p.get_text() for p in paragraphs)

        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        stop_words = {
            'the', 'and', 'to', 'of', 'in', 'a', 'is', 'for', 'on', 'with',
            'that', 'by', 'as', 'it', 'at', 'from', 'this', 'are', 'be',
            'was', 'were', 'have', 'has', 'had', 'but', 'not', 'you', 'they',
            'we', 'she', 'he', 'his', 'her', 'our', 'your', 'my', 'their',
            'will', 'would', 'can', 'could', 'been', 'being'
        }
        filtered = [w for w in words if w not in stop_words]
        common_word = Counter(filtered).most_common(1)[0][0] if filtered else 'N/A'

        tags_container = (
                soup.find('ul', class_='c-meta__list') or
                soup.find('ul', class_='tags') or
                soup.find('div', class_='tags') or
                soup.find('div', class_=re.compile('tag|label'))
        )
        tags = []
        if tags_container:
            for a in tags_container.find_all('a', href=True):
                txt = a.get_text(strip=True)
                if txt:
                    tags.append(txt)

        return {
            'title': title,
            'url': url,
            'word_count': len(words),
            'paragraph_count': len(paragraphs),
            'image_count': len(body.find_all('img')),
            'common_word': common_word,
            'tags': ', '.join(tags) if tags else 'No tags'
        }

    except Exception as e:
        print(f"Ошибка при обработке статьи: {str(e)}")
        return {
            'title': f"Error: {str(e)[:50]}",
            'url': url,
            'word_count': 0,
            'paragraph_count': 0,
            'image_count': 0,
            'common_word': 'N/A',
            'tags': 'Error'
        }

article_urls = [
    'https://www.thenationalnews.com/travel/2025/07/26/anandes-hotel-mykonos-review-greece-island/',
    'https://www.thenationalnews.com/travel/2025/07/17/visiting-uae-during-summer-everything-tourists-need-to-know/',
    'https://www.thenationalnews.com/travel/2025/07/22/chatham-inn-cape-cod-hotel-review/',
    'https://www.thenationalnews.com/travel/2025/07/24/best-staycation-deals-uae-summer-2025/',
    'https://www.thenationalnews.com/travel/2025/07/24/shenzhen-china-destination-museums-parks-technology-halal-dining/'
]

results = []
for url in article_urls:
    results.append(parse_article(url))
    time.sleep(2)

df = pd.DataFrame(results)

print(df.to_markdown(index=False, tablefmt="grid"))
