from flask import Flask, render_template, request
from datetime import datetime
import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bs4 import BeautifulSoup

app = Flask(__name__)

# MongoDB Atlas connection string
connection_string = "mongodb+srv://sbp1784:OBbxnqbZowezp2qX@iwazolab.sksu1fm.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client['fintech']
collection = db['rawData']
collection.create_index('URL', unique=True)

# Define the User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        url = request.form.get('url')

        # Basic input validation for the URL
        if not url.startswith("http"):
            return render_template('index.html', error_message="Invalid URL. Please make sure it starts with 'http' or 'https'.")

        # Check if the URL already exists in the collection
        if collection.find_one({'URL': url}):
            return render_template('index.html', error_message=f"An entry with the URL '{url}' already exists.")

        # Send a request to the URL with a User-Agent header
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text from HTML
        html_text = soup.get_text()

        # Data to be inserted as a document in MongoDB
        document = {
            'URL': url,
            'Content': html_text,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        # Insert the document into the collection
        result = collection.insert_one(document)
        return render_template('index.html', success_message=f"Data saved to MongoDB Atlas with document ID: {result.inserted_id}")

    except requests.exceptions.RequestException as e:
        return render_template('index.html', error_message=f"Request failed: {e}")
    except DuplicateKeyError:
        return render_template('index.html', error_message="Error: An entry with the URL already exists.")
    except Exception as e:
        return render_template('index.html', error_message=f"Error occurred: {e}")

if __name__ == "__main__":
    app.run(debug=True)
