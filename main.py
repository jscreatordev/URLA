from flask import Flask, request, redirect, render_template
import string
import random
import json

app = Flask(__name__)

# Redirect subdomain
@app.before_request
def redirect_subdomain():
    # Redirect shrtz.xademx1.repl.co to shrtz.repl.co
    if request.host == 'shrtz.xademx1.repl.co':
        new_url = request.url.replace('shrtz.xademx1.repl.co', 'shrtz.repl.co')
        return redirect(new_url, code=301)

# Rest of your application routes and logic...


# Define a function to generate a random short URL
def generate_short_url():
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(7))

# Load the URL mappings from the file
with open('mappings.json', 'r') as f:
    url_map = json.load(f)

# Load the list of inappropriate words from the file
inappropriate_words = set()

with open('inappropriate_words.txt', 'r') as f:
    for line in f:
        word = line.strip()
        inappropriate_words.add(word)

# Define the route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Define the route for the URL shortening endpoint
@app.route('/shorten', methods=['POST'])
def shorten():
    # Get the original URL and custom URL from the form
    original_url = request.form['url']
    custom_url = request.form['custom_url']
  
    # Check if the custom URL is inappropriate
    if any(word in custom_url.lower() for word in inappropriate_words):
        return render_template('index.html', error='That custom URL contains inappropriate words.')
      
    # If the custom URL is already taken, show an error message
    if custom_url and custom_url in url_map:
        return render_template('index.html', error='That custom URL is already taken.')

    # If the user did not specify a custom URL, generate a random one
    if not custom_url:
        custom_url = generate_short_url()

    # Add the mapping to the URL mappings dictionary
    url_map[custom_url] = original_url

    # Save the mappings to the file
    with open('mappings.json', 'w') as f:
        json.dump(url_map, f)

    # Show the success page with the shortened URL
    short_url = f'{custom_url}'
    return render_template('success.html', short_url=short_url)

# Define the route for the short URL redirections
@app.route('/<short_url>')
def redirect_url(short_url):
    # Check if the shortened URL is in the mappings dictionary
    if short_url in url_map:
        original_url = url_map[short_url]
        return redirect(original_url)
    else:
        return render_template('index.html', error='That shortened URL does not exist.')

# Set up the app to listen on all IP addresses
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)