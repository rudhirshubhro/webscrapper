from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import html2text
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

def extract_abstract_and_html(item):
    try:
        url = item.get('url')
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            item['error'] = f"Failed to retrieve the page. Status code: {response.status_code}"
            return item

        soup = BeautifulSoup(response.content, 'html.parser')

        abstract_tag = soup.find('div', class_='abstract')
        abstract = abstract_tag.get_text(strip=True) if abstract_tag else ''
        
        h = html2text.HTML2Text()
        h.ignore_links = False  # Set to True if you want to ignore links
        # also get the markdown text
        markdown_text = h.handle(soup.get_text(strip=True))

        item['markdown'] = markdown_text
        item['html'] = soup.prettify()
        item['abstract'] = abstract

        return item
    except Exception as e:
        item['error'] = str(e)
        return item

@app.route('/extract', methods=['POST'])
def extract_multiple():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Please send a list of objects with "url", "abstract_number", and "cortellis_ref_id"'}), 400

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(extract_abstract_and_html, data))

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
