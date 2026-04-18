from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from deck_intr.models import Category, Deck, Like, Favorite
from django.db.models import Q, Count, Sum
from accounts.models import CustomUser
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def my_page_view(request):
    """自分のマイページ"""
    return _user_page_logic(request, request.user)

def user_page_view(request, username):
    """他のユーザーのマイページ"""
    user = get_object_or_404(CustomUser, username=username)
    return _user_page_logic(request, user)

def _user_page_logic(request, target_user):
    my_decks = Deck.objects.filter(
        user=target_user  # ← ここで自分のデッキだけに絞り込む
    ).select_related('user').prefetch_related('categories').annotate(
        likes_count=Count('likes')  # いいね数を集計
    ).order_by('-created_at')[:3]   # いいねが多い順、同数なら新しい順
    decks = my_decks

    # 自分がいいねしたデッキを取得
    liked_decks = Deck.objects.filter(
        likes__user=target_user
    ).select_related('user').prefetch_related('categories').annotate(
        likes_count=Count('likes')
    ).order_by('-likes__created_at')[:3]   # いいねした順
    
    # 統計情報を計算
    total_decks = Deck.objects.filter(user=target_user).count()
    total_likes_count = Deck.objects.filter(
        user=target_user
    ).annotate(
        likes_count=Count('likes')
    ).aggregate(total=Sum('likes_count'))['total'] or 0
    
    # いいねした総数
    total_liked_decks = Deck.objects.filter(likes__user=target_user).count()

    is_own_page = request.user.is_authenticated and request.user == target_user

    # お気に入りしているかどうか
    is_favorited = False
    if request.user.is_authenticated and not is_own_page:
        is_favorited = Favorite.objects.filter(
            user=request.user,
            favorite_user=target_user
        ).exists()
    
    # お気に入り数（このユーザーをお気に入りしている人の数）
    favorites_count = Favorite.objects.filter(favorite_user=target_user).count()
    
    return render(request, 'my_page.html',{'profile_user': target_user,'is_own_page': is_own_page,'is_favorited': is_favorited,'favorites_count': favorites_count,'decks':decks,'my_decks': my_decks,'liked_decks': liked_decks,'total_decks': total_decks,'total_likes': total_likes_count,'total_liked_decks': total_liked_decks,})

@login_required
@require_POST
def toggle_favorite_user(request, username):
    """お気に入りユーザーの追加/削除（AJAX）"""
    try:
        target_user = get_object_or_404(CustomUser, username=username)
        
        # 自分自身をお気に入りできないようにする
        if target_user == request.user:
            return JsonResponse({
                'success': False,
                'error': '自分自身をお気に入りに追加できません'
            }, status=400)
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,           # お気に入りする人
            favorite_user=target_user    # お気に入りされる人（対象ユーザー）
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


def iine_view(request):
    # 自分がいいねしたデッキを取得
    liked_decks = Deck.objects.filter(
        likes__user=request.user
    ).select_related('user').prefetch_related('categories').annotate(
        likes_count=Count('likes')
    ).order_by('-likes__created_at')  # いいねした順
    decks = liked_decks
    return render(request, 'iine.html',{'decks':decks})

def decks_list_view(request):
    my_decks = Deck.objects.all().filter(
        user=request.user  # ← ここで自分のデッキだけに絞り込む
    ).select_related('user').prefetch_related('categories').annotate(
        likes_count=Count('likes')  # いいね数を集計
    ).order_by('-created_at')  # いいねが多い順、同数なら新しい順
    decks = my_decks

    return render(request, 'decks_list.html',{'decks':decks})

# def fav_user_view(request):
#     my_favorites = Favorite.objects.filter(user=request.user).select_related('favorite_user')
#     users_with_decks = []
#     for favorite in my_favorites:
#         fav_user = favorite.favorite_user
        
#         # このユーザーの最新デッキ3件を取得
#         recent_decks = Deck.objects.filter(
#             user=fav_user
#         ).select_related('user').prefetch_related('categories').annotate(
#             likes_count=Count('likes')
#         ).order_by('-created_at')[:3]

#         total_decks = Deck.objects.filter(user=fav_user).count()
        
#         total_likes = Deck.objects.filter(
#             user=fav_user
#         ).annotate(
#             likes_count=Count('likes')
#         ).aggregate(total=Sum('likes_count'))['total'] or 0

#         users_with_decks.append({
#             'user': fav_user,
#             'recent_decks': recent_decks,
#             'favorited_at': favorite.created_at,
#             'total_decks': total_decks,
#             'total_likes': total_likes,
#         })
    
#     context = {
#         'users_with_decks': users_with_decks,
#         'total_favorites': my_favorites.count(),
#     }
#     return render(request, 'fav_user.html',context)
def fav_user_view(request):
    # ログインチェック（念のため）
    if not request.user.is_authenticated:
        return redirect('accounts:login')  # ログインページへリダイレクト
    
    print(f"=== fav_user_view DEBUG ===")
    print(f"Current user: {request.user.username} (ID: {request.user.id})")
    
    # お気に入りを取得
    my_favorites = Favorite.objects.filter(user=request.user).select_related('favorite_user')
    print(f"お気に入り数: {my_favorites.count()}")
    
    users_with_decks = []
    
    for favorite in my_favorites:
        fav_user = favorite.favorite_user
        print(f"Processing user: {fav_user.username}")
        
        # このユーザーの最新デッキ3件を取得
        recent_decks = Deck.objects.filter(
            user=fav_user
        ).select_related('user').prefetch_related('categories').annotate(
            likes_count=Count('likes')
        ).order_by('-created_at')[:3]
        
        # 統計情報を計算
        total_decks = Deck.objects.filter(user=fav_user).count()
        
        total_likes = Deck.objects.filter(
            user=fav_user
        ).annotate(
            likes_count=Count('likes')
        ).aggregate(total=Sum('likes_count'))['total'] or 0
        
        print(f"  total_decks: {total_decks}")
        print(f"  total_likes: {total_likes}")
        print(f"  recent_decks count: {recent_decks.count()}")

        users_with_decks.append({
            'user': fav_user,
            'recent_decks': recent_decks,
            'favorited_at': favorite.created_at,
            'total_decks': total_decks,
            'total_likes': total_likes,
        })
    
    print(f"users_with_decks length: {len(users_with_decks)}")
    
    context = {
        'users_with_decks': users_with_decks,
        'total_favorites': my_favorites.count(),
    }
    
    return render(request, 'fav_user.html', context)

def basic_knowledge_view(request):
    return render(request, 'basic_knowledge.html')

def faq_view(request):
    return render(request, 'faq.html')

