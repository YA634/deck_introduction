from django.urls import path
# from django.contrib.auth.views import baccara_view
from .import views

app_name = 'my_page'

urlpatterns = [
    path('my_page/',views.my_page_view, name='my_page'),
    path('user/<str:username>/favorite/', views.toggle_favorite_user, name='toggle_favorite_user'),
    path('user/<str:username>/', views.user_page_view, name='user_page'),
    path('iine/',views.iine_view, name='iine'),
    path('decks_list/',views.decks_list_view, name='decks_list'),
    path('fav_user/',views.fav_user_view, name='fav_user'),
    path('basic_knowledge/',views.basic_knowledge_view, name='basic_knowledge'),
    path('faq/',views.faq_view, name='faq'),
]