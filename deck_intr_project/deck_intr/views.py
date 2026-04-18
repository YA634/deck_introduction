from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from accounts.models import CustomUser
from .models import Category, Deck, Like
from .forms import DeckForm, DeckSearchForm
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from .models import Favorite
from accounts.models import CustomUser

def index_view(request):
    queryset = Deck.objects.all().select_related('user').prefetch_related('categories').annotate(
        likes_count=Count('likes')  # いいね数を集計
    ).order_by('-likes_count', '-created_at')  # いいねが多い順、同数なら新しい順
    decks = queryset

    total_decks = Deck.objects.count()
    total_users = CustomUser.objects.count()
    total_likes = Deck.objects.annotate(likes_count=Count('likes')).aggregate(total=Sum('likes_count'))['total'] or 0

    return render(request, 'index.html',{'decks':decks, 'total_decks':total_decks,'total_users':total_users, 'total_likes':total_likes})



# デッキ詳細ビュー
class DeckDetailView(DetailView):
    model = Deck
    template_name = 'deck_detail.html'
    context_object_name = 'deck'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deck = self.get_object()
        context['likes_count'] = deck.likes_count()
        context['is_liked'] = deck.is_liked_by(self.request.user)
        return context

# デッキ作成（複数カテゴリー選択可能）
class DeckCreateView(LoginRequiredMixin, CreateView):
    model = Deck
    form_class = DeckForm
    template_name = 'deck_form.html'
    success_url = reverse_lazy('deck_intr:index')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


# いいね機能（AJAX）
@login_required
@require_POST
def toggle_like(request, deck_id):
    try:
        deck = get_object_or_404(Deck, id=deck_id)
        
        # いいねが既に存在するか確認
        like, created = Like.objects.get_or_create(deck=deck, user=request.user)
        
        if not created:
            # 既にいいねしている場合は削除（いいね解除）
            like.delete()
            is_liked = False
        else:
            # いいねを新規作成
            is_liked = True
        
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'likes_count': deck.likes_count()
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_POST
def add_category_ajax(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        slug = data.get('slug', '').strip()
        
        if not name or not slug:
            return JsonResponse({
                'success': False,
                'error': 'カテゴリー名とスラッグの両方を入力してください'
            }, status=400)
        
        # カテゴリーを作成（既存の場合はエラー）
        if Category.objects.filter(slug=slug).exists():
            return JsonResponse({
                'success': False,
                'error': 'このスラッグは既に使用されています'
            }, status=400)
        
        category = Category.objects.create(name=name, slug=slug)
        
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '不正なリクエストです'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_POST
def toggle_favorite(request, user_id):
    """お気に入りユーザーの追加/削除（AJAX）"""
    try:
        target_user = get_object_or_404(CustomUser, id=user_id)
        
        # 自分自身をお気に入りできないようにする
        if target_user == request.user:
            return JsonResponse({
                'success': False,
                'error': '自分自身をお気に入りに追加できません'
            }, status=400)
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            favorite_user=target_user
        )
        
        if not created:
            # 既にお気に入りの場合は削除
            favorite.delete()
            is_favorited = False
        else:
            is_favorited = True
        
        # お気に入り数を取得
        favorites_count = Favorite.objects.filter(favorite_user=target_user).count()
        
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'favorites_count': favorites_count
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

class DeckSearchView(ListView):
    model = Deck
    template_name = 'deck_search.html'
    context_object_name = 'decks'
    paginate_by = 12  # 1ページあたりの表示件数
    
    def get_queryset(self):
        queryset = Deck.objects.all().select_related('user').prefetch_related('categories')
        
        # フォームからデータ取得
        form = DeckSearchForm(self.request.GET)
        
        if form.is_valid():
            # キーワード検索（タイトルと本文を検索）
            keyword = form.cleaned_data.get('keyword')
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) | Q(text__icontains=keyword)
                )
            
            # カテゴリーで絞り込み
            categories = form.cleaned_data.get('categories')
            if categories:
                queryset = queryset.filter(categories__in=categories).distinct()
            
            # 投稿者で絞り込み
            username = form.cleaned_data.get('username')
            if username:
                queryset = queryset.filter(user__username__icontains=username)
            
            # 並び順
            order = form.cleaned_data.get('order')
            if order:
                queryset = queryset.order_by(order)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeckSearchForm(self.request.GET)
        context['total_count'] = self.get_queryset().count()
        return context
    
class RankingView(ListView):
    model = Deck
    template_name = 'ranking.html'
    context_object_name = 'decks'
    paginate_by = 10  # 1ページあたりの表示件数
    
    def get_queryset(self):
        # likes_countを集計してから並び替え
        queryset = Deck.objects.all().select_related('user').prefetch_related('categories').annotate(
            likes_count=Count('likes')  # いいね数を集計
        ).order_by('-likes_count', '-created_at')  # いいねが多い順、同数なら新しい順
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeckSearchForm(self.request.GET)
        context['total_count'] = self.get_queryset().count()
        return context