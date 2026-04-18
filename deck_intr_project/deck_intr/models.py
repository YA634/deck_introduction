from django.db import models
from django.conf import settings
from .consts import MAX_RATE

RATE_CHOICES = [(x,str(x)) for x in range(0, MAX_RATE + 1)]
# Create your models here.

# class SampleModel(models.Model):
#     title = models.CharField(max_length=100)
#     number = models.IntegerField()
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='カテゴリー名')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='スラッグ（英数字）')
    
    class Meta:
        verbose_name = 'カテゴリー'
        verbose_name_plural = 'カテゴリー'
    
    def __str__(self):
        return self.name
    
# CATEGORY = (('special-win','特殊勝利'),('first-turn-win','先行ワンキル'),('turn-skip','ターンスキップ'),('3-axis','3軸初動'),('seed-loop','種ループ'),('golgar-loop','ゴルガーループ'),('none-loop','ループ無し'))

class Deck(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    thumbnail = models.ImageField(null=True, blank=True)
    video = models.FileField(null=True, blank=True, upload_to='videos/', verbose_name='動画')
    categories = models.ManyToManyField(
        Category,
        verbose_name='カテゴリー',
        blank=True
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    # いいね数を取得するメソッド
    def likes_count(self):
        return self.likes.count()
    
    # 特定のユーザーがいいねしているか確認
    def is_liked_by(self, user):
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False


class Like(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # 同じユーザーが同じデッキに複数回いいねできないようにする
        unique_together = ('deck', 'user')
        verbose_name = 'いいね'
        verbose_name_plural = 'いいね'
    
    def __str__(self):
        return f'{self.user.username} -> {self.deck.title}'

class Favorite(models.Model):
    favorite_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_user')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('favorite_user', 'user')
        verbose_name = 'お気に入りユーザー'
        verbose_name_plural = 'お気に入りユーザー'
    
    def __str__(self):
        return f'{self.user.username} -> {self.favorite_user.username}'

class Review(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    rate = models.IntegerField(choices=RATE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title