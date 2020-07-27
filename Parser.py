from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup



def get_page(url):
    r = requests.get(url)
    return r.content

def parse_text(url):
    soup = BeautifulSoup(get_page(url), 'html.parser')

    # удаляем все элементы script и style
    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()

    # удаляем лишние пробелы и разделяем текстовые элементы на строки
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

def get_internal_links(url, pages):
    DOMAIN = url[7:]
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    for tag_a in soup.find_all('a', href=lambda v: v is not None):
        link = tag_a['href']

        # если ссылка не начинается с одного из запрещённых префиксов
        if all(not link.startswith(prefix) for prefix in ['#', 'tel:', 'mailto:']):
            if link.startswith("https://www."):
                link = "http://" + link[12:]
            if link.startswith('/') and not link.startswith('//') and link[-3:] not in ['doc', 'pdf']:
                link = url + link
            # проверяем, что ссылка ведёт на нужный домен
            # и что мы ещё не обрабатывали такую ссылку
            if urlparse(link).netloc == DOMAIN and link not in pages:
                pages.append(link)
                get_internal_links(link, pages)


# запускаем парсер
def parser(url):
    pages = []
    url = "http://" + url
    get_internal_links(url, pages)
    text = ''
    for page in pages:
        text = text + parse_text(page)

    return text


