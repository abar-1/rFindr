import beutifulsoup4 as bs
import requests

class WebScraper:

    def __init__(self):
        pass
    
    def scrape_webpage(self, url: str) -> str:

        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to load {url}")

        soup = bs.BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text_content = '\n'.join([para.get_text() for para in paragraphs])

        return text_content