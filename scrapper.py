import logging
import requests
from bs4 import BeautifulSoup

def scrap_website_data(url):

    try:
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the body tag
        body_tag = soup.body

        # Extract text with hierarchical structure from the body tag
        plain_text_with_hierarchy = body_tag.get_text(separator='\n', strip=True)

        # Print or process the extracted text
        return plain_text_with_hierarchy
    except Exception as e:
        logging.error(e)
        raise e
