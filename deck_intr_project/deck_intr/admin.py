from django.contrib import admin
from .models import Deck, Review, Category, Like, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # nameから自動でslugを生成

@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'get_categories']
    filter_horizontal = ['categories']  # カテゴリー選択を見やすく
    
    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = 'カテゴリー'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'deck', 'rate', 'user']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'deck', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'deck__title']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'favorite_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'favorite_user__username', 'favorite_user__email')
    date_hierarchy = 'created_at'