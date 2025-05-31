from django.urls import path
from . import views

urlpatterns = [
    path('quotes/random', views.get_random_quote, name='random_quote'),
    path('quotes/category/<str:category>', views.get_quotes_by_category, name='quotes_by_category'),
    path('quotes', views.get_all_quotes, name='all_quotes'),
    path('quotes/categories', views.get_categories, name='categories'),
]