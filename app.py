from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

def extract_ash_paper_info(url):
    response = requests.get(url)
    if response.status_code != 200:
        return {'error': f"Failed to retrieve the page. Status code: {response.status_code}"}

    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h2').get_text(strip=True) if soup.find('h2') else 'Title not found'
    session_tag = soup.find('div', class_='session')
    session_info = session_tag.get_text(strip=True) if session_tag else ''
    authors = [tag.get_text(strip=True) for tag in soup.find_all('span', class_='author')]
    abstract_tag = soup.find('div', class_='abstract')
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else ''
    full_html = soup.prettify()

    return {
        # 'title': title,
        # 'session': session_info,
        # 'authors': authors,
        'sourceUrl': url,
        'abstract': abstract,
        'html': full_html
    }

@app.route('/extract', methods=['POST'])
def extract_multiple():
    data = request.get_json()
    urls = data.get('urls') if data else None

    if not urls or not isinstance(urls, list):
        return jsonify({'error': 'Please provide a list of URLs in the "urls" field'}), 400

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(extract_ash_paper_info, urls))

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
