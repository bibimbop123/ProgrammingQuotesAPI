import os
import json
import random
import logging
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Enable CORS for all routes
CORS(app)

# Load quotes data
def load_quotes():
    """Load quotes from JSON file"""
    try:
        with open('data/quotes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        app.logger.error("Quotes data file not found")
        return {"quotes": []}
    except json.JSONDecodeError:
        app.logger.error("Invalid JSON in quotes data file")
        return {"quotes": []}

# API Routes
@app.route('/')
def index():
    """Serve API documentation page"""
    return render_template('index.html')

@app.route('/api/quotes/random', methods=['GET'])
def get_random_quote():
    """Get a random programming quote"""
    try:
        quotes_data = load_quotes()
        quotes = quotes_data.get('quotes', [])
        
        if not quotes:
            return jsonify({
                'error': 'No quotes available',
                'message': 'The quotes database is empty'
            }), 404
        
        random_quote = random.choice(quotes)
        return jsonify({
            'quote': random_quote['text'],
            'author': random_quote['author'],
            'category': random_quote.get('category', 'general')
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error getting random quote: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve random quote'
        }), 500

@app.route('/api/quotes/category/<category>', methods=['GET'])
def get_quotes_by_category(category):
    """Get quotes by category/topic"""
    try:
        quotes_data = load_quotes()
        quotes = quotes_data.get('quotes', [])
        
        # Filter quotes by category (case-insensitive)
        filtered_quotes = [
            quote for quote in quotes 
            if quote.get('category', '').lower() == category.lower()
        ]
        
        if not filtered_quotes:
            return jsonify({
                'error': 'No quotes found',
                'message': f'No quotes found for category: {category}',
                'available_categories': list(set(
                    quote.get('category', 'general').lower() 
                    for quote in quotes
                ))
            }), 404
        
        # Format response
        response_quotes = [
            {
                'quote': quote['text'],
                'author': quote['author'],
                'category': quote.get('category', 'general')
            }
            for quote in filtered_quotes
        ]
        
        return jsonify({
            'category': category,
            'count': len(response_quotes),
            'quotes': response_quotes
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error getting quotes by category: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': f'Failed to retrieve quotes for category: {category}'
        }), 500

@app.route('/api/quotes', methods=['GET'])
def get_all_quotes():
    """Get all quotes with pagination"""
    try:
        quotes_data = load_quotes()
        quotes = quotes_data.get('quotes', [])
        
        if not quotes:
            return jsonify({
                'error': 'No quotes available',
                'message': 'The quotes database is empty'
            }), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validate pagination parameters
        if page < 1:
            return jsonify({
                'error': 'Invalid page number',
                'message': 'Page number must be greater than 0'
            }), 400
        
        if per_page < 1 or per_page > 100:
            return jsonify({
                'error': 'Invalid per_page value',
                'message': 'per_page must be between 1 and 100'
            }), 400
        
        # Calculate pagination
        total_quotes = len(quotes)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        if start_index >= total_quotes:
            return jsonify({
                'error': 'Page not found',
                'message': f'Page {page} does not exist',
                'total_pages': (total_quotes + per_page - 1) // per_page
            }), 404
        
        paginated_quotes = quotes[start_index:end_index]
        
        # Format response
        response_quotes = [
            {
                'quote': quote['text'],
                'author': quote['author'],
                'category': quote.get('category', 'general')
            }
            for quote in paginated_quotes
        ]
        
        return jsonify({
            'quotes': response_quotes,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_quotes,
                'total_pages': (total_quotes + per_page - 1) // per_page,
                'has_next': end_index < total_quotes,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error getting all quotes: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve quotes'
        }), 500

@app.route('/api/quotes/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    try:
        quotes_data = load_quotes()
        quotes = quotes_data.get('quotes', [])
        
        if not quotes:
            return jsonify({
                'error': 'No quotes available',
                'message': 'The quotes database is empty'
            }), 404
        
        # Extract unique categories
        categories = list(set(
            quote.get('category', 'general').lower() 
            for quote in quotes
        ))
        categories.sort()
        
        return jsonify({
            'categories': categories,
            'count': len(categories)
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error getting categories: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve categories'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The requested method is not allowed for this endpoint'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
