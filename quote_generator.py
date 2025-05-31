import json
import random
import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

def load_quotes():
    """Load quotes from JSON file"""
    try:
        with open('data/quotes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"quotes": []}
    except json.JSONDecodeError:
        return {"quotes": []}

def get_random_quote():
    """Get a random quote from the quotes data"""
    try:
        quotes_data = load_quotes()
        quotes = quotes_data.get('quotes', [])
        
        if not quotes:
            return None
        
        random_quote = random.choice(quotes)
        return {
            'quote': random_quote['text'],
            'author': random_quote['author'],
            'category': random_quote.get('category', 'general')
        }
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return None

def get_categories():
    """Get all available categories"""
    try:
        quotes_data = load_quotes()
        quotes = quotes_data.get('quotes', [])
        
        if not quotes:
            return []
        
        # Extract unique categories
        categories = list(set(
            quote.get('category', 'general').lower() 
            for quote in quotes
        ))
        categories.sort()
        return categories
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

def get_quote_by_category(category):
    """Get a random quote by category"""
    try:
        quotes_data = load_quotes()
        quotes = quotes_data.get('quotes', [])
        
        # Filter quotes by category (case-insensitive)
        filtered_quotes = [
            quote for quote in quotes 
            if quote.get('category', '').lower() == category.lower()
        ]
        
        if not filtered_quotes:
            return None
            
        random_quote = random.choice(filtered_quotes)
        return {
            'quote': random_quote['text'],
            'author': random_quote['author'],
            'category': random_quote.get('category', 'general')
        }
    except Exception as e:
        print(f"Error fetching quote by category: {e}")
        return None

@app.route('/')
def index():
    """Main page - Quote Generator"""
    return render_template('quote_generator.html')

@app.route('/api/generate-quote')
def generate_quote():
    """Generate a random quote"""
    quote = get_random_quote()
    if quote:
        return jsonify(quote)
    else:
        return jsonify({'error': 'Failed to fetch quote'}), 500

@app.route('/api/categories')
def api_categories():
    """Get all categories"""
    categories = get_categories()
    return jsonify({'categories': categories})

@app.route('/api/generate-quote/<category>')
def generate_quote_by_category(category):
    """Generate a quote by category"""
    quote = get_quote_by_category(category)
    if quote:
        return jsonify(quote)
    else:
        return jsonify({'error': f'Failed to fetch quote for category: {category}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)