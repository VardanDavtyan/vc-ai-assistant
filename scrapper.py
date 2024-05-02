import logging
import requests
from bs4 import BeautifulSoup

def scrap_website_data(url):

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(url, headers=headers)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        plain_text_with_hierarchy = f"website title: {soup.title.text}\nwebsite scrapped content: "

        # Find the body tag
        body_tag = soup.body
        # Extract text with hierarchical structure from the body tag
        plain_text_with_hierarchy += body_tag.get_text(separator='\n', strip=True)

        # Print or process the extracted text
        return plain_text_with_hierarchy
    except Exception as e:
        logging.error(e)
        raise e
