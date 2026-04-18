from django.urls import path,include
from .import views
from .views import (
    DeckCreateView, 
    DeckSearchView, 
    DeckDetailView,
    RankingView,
    add_category_ajax,
    toggle_like
)

app_name = 'deck_intr'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('decks/create/', DeckCreateView.as_view(), name='deck_create'),
    path('decks/search/', DeckSearchView.as_view(), name='deck_search'),
    path('decks/ranking/', RankingView.as_view(), name='ranking'),
    path('decks/<int:pk>/', DeckDetailView.as_view(), name='deck_detail'),
    path('decks/<int:deck_id>/like/', toggle_like, name='toggle_like'),
    path('categories/add-ajax/', add_category_ajax, name='add_category_ajax'),
]