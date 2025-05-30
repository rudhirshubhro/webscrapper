from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

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

    return {
        'title': title,
        'session': session_info,
        'authors': authors,
        'abstract': abstract
    }

@app.route('/extract', methods=['GET'])
def extract():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    return jsonify(extract_ash_paper_info(url))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
