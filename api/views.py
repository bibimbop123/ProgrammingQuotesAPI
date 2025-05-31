import json
import random
import os
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

def load_quotes():
    """Load quotes from JSON file"""
    try:
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'quotes.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"quotes": []}
    except json.JSONDecodeError:
        return {"quotes": []}

def index(request):
    """Serve API documentation page"""
    return render(request, 'index.html')

@api_view(['GET'])
def get_random_quote(request):
    """Get a random programming quote"""
    try:
        quotes_data = load_quotes()
        quotes = quotes_data.get('quotes', [])
        
        if not quotes:
            return Response({
                'error': 'No quotes available',
                'message': 'The quotes database is empty'
            }, status=status.HTTP_404_NOT_FOUND)
        
        random_quote = random.choice(quotes)
        return Response({
            'quote': random_quote['text'],
            'author': random_quote['author'],
            'category': random_quote.get('category', 'general')
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'message': 'Failed to retrieve random quote'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_quotes_by_category(request, category):
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
            return Response({
                'error': 'No quotes found',
                'message': f'No quotes found for category: {category}',
                'available_categories': list(set(
                    quote.get('category', 'general').lower() 
                    for quote in quotes
                ))
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Format response
        response_quotes = [
            {
                'quote': quote['text'],
                'author': quote['author'],
                'category': quote.get('category', 'general')
            }
            for quote in filtered_quotes
        ]
        
        return Response({
            'category': category,
            'count': len(response_quotes),
            'quotes': response_quotes
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'message': f'Failed to retrieve quotes for category: {category}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuotesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'per_page'
    max_page_size = 100

@api_view(['GET'])
def get_all_quotes(request):
    """Get all quotes with pagination"""
    try:
        quotes_data = load_quotes()
        quotes = quotes_data.get('quotes', [])
        
        if not quotes:
            return Response({
                'error': 'No quotes available',
                'message': 'The quotes database is empty'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get pagination parameters
        try:
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 10))
        except ValueError:
            return Response({
                'error': 'Invalid parameters',
                'message': 'Page and per_page must be valid integers'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate pagination parameters
        if page < 1:
            return Response({
                'error': 'Invalid page number',
                'message': 'Page number must be greater than 0'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if per_page < 1 or per_page > 100:
            return Response({
                'error': 'Invalid per_page value',
                'message': 'per_page must be between 1 and 100'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate pagination
        total_quotes = len(quotes)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        if start_index >= total_quotes:
            return Response({
                'error': 'Page not found',
                'message': f'Page {page} does not exist',
                'total_pages': (total_quotes + per_page - 1) // per_page
            }, status=status.HTTP_404_NOT_FOUND)
        
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
        
        return Response({
            'quotes': response_quotes,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_quotes,
                'total_pages': (total_quotes + per_page - 1) // per_page,
                'has_next': end_index < total_quotes,
                'has_prev': page > 1
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'message': 'Failed to retrieve quotes'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_categories(request):
    """Get all available categories"""
    try:
        quotes_data = load_quotes()
        quotes = quotes_data.get('quotes', [])
        
        if not quotes:
            return Response({
                'error': 'No quotes available',
                'message': 'The quotes database is empty'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Extract unique categories
        categories = list(set(
            quote.get('category', 'general').lower() 
            for quote in quotes
        ))
        categories.sort()
        
        return Response({
            'categories': categories,
            'count': len(categories)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'message': 'Failed to retrieve categories'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)