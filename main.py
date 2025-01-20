from flask import Flask, request, redirect, render_template, jsonify
import string
import random
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def generate_short_url():
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(7))

# Load existing URL mappings
with open('mappings.json', 'r') as f:
    url_map = json.load(f)

# Load inappropriate words
inappropriate_words = set()
with open('inappropriate_words.txt', 'r') as f:
    for line in f:
        word = line.strip()
        inappropriate_words.add(word)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form['url']
    custom_url = request.form['custom_url']

    if any(word in custom_url.lower() for word in inappropriate_words):
        return render_template('index.html', error='That custom URL contains inappropriate words.')

    if custom_url and custom_url in url_map:
        return render_template('index.html', error='That custom URL is already taken.')

    if not custom_url:
        custom_url = generate_short_url()

    if not original_url.startswith(('http://', 'https://')):
        original_url = 'http://' + original_url

    url_map[custom_url] = original_url

    with open('mappings.json', 'w') as f:
        json.dump(url_map, f)

    with open('links.txt', 'a') as f:
        f.write("https://your-vercel-app.vercel.app/" + custom_url + ':' + original_url + '\n')

    short_url = f'{custom_url}'
    return render_template('success.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_url(short_url):
    if short_url in url_map:
        original_url = url_map[short_url]
        return redirect(original_url)
    else:
        return render_template('index.html', error='That shortened URL does not exist.')

# API Endpoint to allow external requests
@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    data = request.get_json()
    original_url = data.get('url')
    custom_url = data.get('custom_url')

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    if any(word in custom_url.lower() for word in inappropriate_words):
        return jsonify({"error": "Custom URL contains inappropriate words"}), 400

    if custom_url and custom_url in url_map:
        return jsonify({"error": "Custom URL is already taken"}), 400

    if not custom_url:
        custom_url = generate_short_url()

    if not original_url.startswith(('http://', 'https://')):
        original_url = 'http://' + original_url

    url_map[custom_url] = original_url

    with open('mappings.json', 'w') as f:
        json.dump(url_map, f)

    short_url = f'{custom_url}'
    return jsonify({"short_url": f"https://your-vercel-app.vercel.app/{short_url}"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
